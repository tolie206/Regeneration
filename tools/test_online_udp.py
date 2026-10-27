import subprocess,socket,time,sys,struct,os
probe=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);probe.bind(('127.0.0.1',0));port=probe.getsockname()[1];probe.close()
env=dict(os.environ);env['MUGOAT_BIND']='127.0.0.1'
p=subprocess.Popen([sys.argv[1],str(port),'2'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=0x08000000 if os.name=='nt' else 0)
def client(name,room='roleplay'):
 s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('127.0.0.1',port));s.settimeout(.6)
 for _ in range(20):
  s.send(bytes([0x47,1])+room.encode()+b'\0'+name.encode())
  try:
   while True:
    d=s.recv(1600)
    if d[:2]==bytes([0x47,2]):return s,d[2]
  except (socket.timeout,ConnectionResetError,ConnectionRefusedError):
   if p.poll() is not None:raise AssertionError("server exited: "+p.stderr.read().decode(errors="replace"))
   time.sleep(.05)
 raise AssertionError('server welcome missing')
def drain(s):
 s.settimeout(.05)
 try:
  while True:s.recv(1600)
 except socket.timeout:pass
 s.settimeout(.4)
try:
 a,aid=client('Alice');b,bid=client('Bob');assert aid!=bid
 drain(a);drain(b)
 shot=struct.pack('<I6f',0,1,2,3,4,5,6);a.send(bytes([0x47,9])+shot)
 d=b.recv(1600);assert d==bytes([0x47,9,aid])+shot
 for kind in [24,25,26,27,28,29,255]:
  a.send(bytes([0x47,kind,1,2,3]));a.send(bytes([0x47,19,0,1,0,kind,1,2,3]))
 try:b.recv(1600);raise AssertionError('untrusted RP event forwarded')
 except socket.timeout:pass
 a.send(bytes([0x47,6]));time.sleep(.1)
 c,cid=client('AliceAgain');assert cid!=bid
 for s in [a,b,c]:s.close()
 print('PASS real loopback server: two players, sender identity, relay, denied RP commands, reconnect')
finally:
 p.terminate();p.wait(timeout=5)
