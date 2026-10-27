// muguet - server.rs
// Constantin Clerc (c22dev) - 0.1

use crate::proto::*;
use std::collections::HashMap;
use std::net::{SocketAddr, UdpSocket};
use std::time::{Duration, Instant};

struct Player {
    id: u8,
    room: String,
    name: String,
    last: Instant,
}

pub fn run(port: u16, max: usize) -> std::io::Result<()> {
    let max = max.clamp(2, MAX_ROOM_PLAYERS);
    let sock = UdpSocket::bind((std::env::var("MUGOAT_BIND").unwrap_or_else(|_|"127.0.0.1".into()), port))?;
    sock.set_read_timeout(Some(Duration::from_millis(500)))?;
    println!("[server] listening on UDP port {port} (up to {max} players per room)");
    for ip in local_ips() {
        println!("[server] players on this network join with {ip}:{port}");
    }

    let mut players: HashMap<SocketAddr, Player> = HashMap::new();
    let mut buf = [0u8; 1500];
    let mut last_sweep = Instant::now();
    loop {
        match sock.recv_from(&mut buf) {
            Ok((n, from)) => {
                if let Some((kind, payload)) = parse(&buf[..n]) {
                    handle(&sock, &mut players, max, from, kind, payload);
                }
            }
            Err(e) if matches!(e.kind(), std::io::ErrorKind::WouldBlock | std::io::ErrorKind::TimedOut) => {}
            Err(e) => eprintln!("[server] recv: {e}"),
        }
        if last_sweep.elapsed() >= Duration::from_secs(2) {
            last_sweep = Instant::now();
            let gone: Vec<SocketAddr> = players.iter().filter(|(_, p)| p.last.elapsed() > Duration::from_secs(TIMEOUT_SECS)).map(|(a, _)| *a).collect();
            for addr in gone {
                leave(&sock, &mut players, addr, "timed out");
            }

            for (addr, p) in &players {
                for (to, _) in players.iter().filter(|(a, peer)| *a != addr && peer.room == p.room) {
                    let _ = sock.send_to(&name_packet(p), to);
                }
            }
        }
    }
}

fn name_packet(p: &Player) -> Vec<u8> {
    let mut payload = vec![p.id];
    payload.extend(p.name.as_bytes());
    packet(NAME, &payload)
}

fn parse_room_and_name(payload: &[u8]) -> (String, String) {
    if let Some(pos) = payload.iter().position(|&b| b == 0) {
        let room_str = String::from_utf8_lossy(&payload[..pos]).trim().to_lowercase();
        let name_str = clean_name(&payload[pos + 1..]);
        let room = if room_str.is_empty() { "default".to_string() } else { room_str };
        (room, name_str)
    } else {
        ("default".to_string(), clean_name(payload))
    }
}

fn handle(sock: &UdpSocket, players: &mut HashMap<SocketAddr, Player>, max: usize, from: SocketAddr, kind: u8, payload: &[u8]) {
    if !allowed_packet(kind,payload,0) { return; }
    match kind {
        HELLO => {
            if players.len()>=256&&!players.contains_key(&from){let _=sock.send_to(&packet(FULL,&[]),from);return;}
            let (room, name) = parse_room_and_name(payload);
            if let Some(p) = players.get_mut(&from).filter(|p| p.room == room) {
                p.last = Instant::now();
                p.name = name;
                let _ = sock.send_to(&packet(WELCOME, &[p.id]), from);
                return;
            }
            let room_count = players.values().filter(|p| p.room == room).count();
            if room_count >= max {
                let _ = sock.send_to(&packet(FULL, &[]), from);
                return;
            }
            // A socket changing rooms must re-enter capacity/ID allocation,
            // rather than keeping an ID which may already exist in that room.
            if players.contains_key(&from) {
                leave(sock, players, from, "changed rooms");
            }
            let id = (1..=255u8).find(|i| !players.values().any(|p| p.room == room && p.id == *i)).unwrap();
            let p = Player { id, room: room.clone(), name, last: Instant::now() };
            println!("[server] {} joined room [{}] as player {id} from {from} ({} in room, {} total online)", p.name, p.room, room_count + 1, players.len() + 1);
            let _ = sock.send_to(&packet(WELCOME, &[id]), from);
            for (addr, other) in players.iter().filter(|(_, other)| other.room == room) {
                let _ = sock.send_to(&name_packet(other), from);
                let _ = sock.send_to(&name_packet(&p), addr);
            }
            players.insert(from, p);
        }
        kind if relayed(kind) => {
            let (id, room) = {
                let Some(p) = players.get_mut(&from) else {
                    let _ = sock.send_to(&packet(LEAVE, &[0]), from);
                    return;
                };
                p.last = Instant::now();
                (p.id, p.room.clone())
            };
            let mut out = vec![id];
            out.extend_from_slice(payload);
            let pkt = packet(kind, &out);
            for (addr, peer) in players.iter() {
                if *addr != from && peer.room == room {
                    let _ = sock.send_to(&pkt, addr);
                }
            }
        }
        BYE => leave(sock, players, from, "left"),
        _ => {}
    }
}

fn leave(sock: &UdpSocket, players: &mut HashMap<SocketAddr, Player>, addr: SocketAddr, why: &str) {
    if let Some(p) = players.remove(&addr) {
        println!("[server] {} in room [{}] {why} ({} total online)", p.name, p.room, players.len());
        for (to, peer) in players.iter() {
            if peer.room == p.room {
                let _ = sock.send_to(&packet(LEAVE, &[p.id]), to);
            }
        }
    }
}

fn local_ips() -> Vec<String> {
    let run = |cmd: &str, args: &[&str]| std::process::Command::new(cmd).args(args).output().map(|o| String::from_utf8_lossy(&o.stdout).into_owned()).unwrap_or_default();
    let mut out = run("/sbin/ifconfig", &[]);
    if out.is_empty() {
        out = run("ip", &["-4", "-o", "addr", "show"]).replace(" inet ", "\ninet ");
    }
    out.lines()
        .filter_map(|l| l.trim().strip_prefix("inet "))
        .filter_map(|l| l.split_whitespace().next())
        .map(|ip| ip.split('/').next().unwrap_or(ip))
        .filter(|ip| !ip.starts_with("127."))
        .map(String::from)
        .collect()
}

fn allowed_packet(kind:u8,p:&[u8],depth:u8)->bool{
 if p.len()>1400||depth>0&&kind==REL{return false}
 match kind{
  HELLO=>!p.is_empty()&&p.len()<=113,
  BYE=>p.is_empty(),
  STATE=>State::decode(p).map(|s|s.pos.iter().chain(s.vel.iter()).chain(s.veh_pos.iter()).chain(s.veh_rot.iter()).chain(s.veh_vel.iter()).chain(s.aim.iter()).all(|v|v.is_finite()&&v.abs()<100000.0)&&s.heading.is_finite()&&s.health<=1000).unwrap_or(false),
  LOOK=>Look::decode(p).is_some(),VLOOK=>VehLook::decode(p).is_some(),
  REL=>p.len()>=4&&allowed_packet(p[3],&p[4..],depth+1),
  ACK=>p.len()==3,
  VOICE=>VoiceChunk::decode(p).is_some(),
  SHOT=>Shot::decode(p).is_some(),
  HIT|VHIT|KILL|VCTL|TAKEN=>!p.is_empty()&&p.len()<128,
  TIME=>p.len()<64&&!p.is_empty(),
  _=>false,
 }
}
#[cfg(test)] mod rp_policy_tests{
 use super::*;
 #[test] fn rejects_legacy_client_economy_roles_and_nested_abuse(){
  for k in [ROLE,ARREST,HEAL,ROB,PAID,255]{assert!(!allowed_packet(k,&[1,2,3],0));assert!(!allowed_packet(REL,&[0,1,0,k,1,2,3],0));}
  assert!(!allowed_packet(REL,&[0,1,0,REL,0,1,0,STATE],0));
 }
 #[test] fn rejects_oversized_and_empty_state(){assert!(!allowed_packet(HELLO,&[0;114],0));assert!(!allowed_packet(STATE,&[],0));assert!(allowed_packet(HELLO,b"roleplay\0Tester",0));}
}
