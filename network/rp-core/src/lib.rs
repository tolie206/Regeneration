//! Authoritative RP domain core. No client-supplied balance, reward or admin flag is accepted.
//! Account authentication and gameplay RPC are separate milestones, not simulated here.
use rusqlite::{Connection,params,OptionalExtension};
pub struct Core{db:Connection}
impl Core{
 pub fn open(path:&str)->rusqlite::Result<Self>{
  let db=Connection::open(path)?;db.busy_timeout(std::time::Duration::from_secs(5))?;
  db.execute_batch("PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;
  CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
  INSERT OR IGNORE INTO schema_version VALUES(1);
  CREATE TABLE IF NOT EXISTS characters(id TEXT PRIMARY KEY,name TEXT NOT NULL,cash INTEGER NOT NULL DEFAULT 0 CHECK(cash>=0),bank INTEGER NOT NULL DEFAULT 0 CHECK(bank>=0));
  CREATE TABLE IF NOT EXISTS receipts(id TEXT NOT NULL,actor TEXT NOT NULL,operation TEXT NOT NULL,PRIMARY KEY(actor,id));
  CREATE TABLE IF NOT EXISTS inventory(owner TEXT NOT NULL REFERENCES characters(id),item TEXT NOT NULL,quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 1000000),PRIMARY KEY(owner,item));
  CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,owner TEXT NOT NULL REFERENCES characters(id),completed INTEGER NOT NULL DEFAULT 0);")?;
  Ok(Self{db})
 }
 pub fn create_character(&self,id:&str,name:&str)->rusqlite::Result<bool>{
  if id.is_empty()||id.len()>64||name.is_empty()||name.len()>64{return Ok(false)}
  Ok(self.db.execute("INSERT OR IGNORE INTO characters(id,name) VALUES(?1,?2)",params![id,name])?==1)
 }
 pub fn balance(&self,id:&str)->rusqlite::Result<Option<(i64,i64)>>{self.db.query_row("SELECT cash,bank FROM characters WHERE id=?1",[id],|r|Ok((r.get(0)?,r.get(1)?))).optional()}
 // Admin-only provisioning API: never directly exposed as a public player RPC.
 pub fn admin_grant(&self,id:&str,cash:i64)->rusqlite::Result<bool>{
  if cash<=0||cash>1_000_000{return Ok(false)}
  Ok(self.db.execute("UPDATE characters SET cash=cash+?1 WHERE id=?2 AND cash<=9000000000000000-?1",params![cash,id])?==1)
 }
 pub fn deposit(&mut self,actor:&str,amount:i64,request:&str)->rusqlite::Result<bool>{
  if amount<=0||request.is_empty()||request.len()>128{return Ok(false)}
  let tx=self.db.transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)?;
  if tx.query_row("SELECT 1 FROM receipts WHERE id=?1 AND actor=?2",params![request,actor],|r|r.get::<_,i32>(0)).optional()?.is_some(){return Ok(false)}
  if tx.execute("UPDATE characters SET cash=cash-?1,bank=bank+?1 WHERE id=?2 AND cash>=?1 AND bank<=9000000000000000-?1",params![amount,actor])?!=1{return Ok(false)}
  tx.execute("INSERT INTO receipts VALUES(?1,?2,'deposit')",params![request,actor])?;tx.commit()?;Ok(true)
 }
 pub fn transfer_item(&mut self,actor:&str,to:&str,item:&str,count:i64,request:&str)->rusqlite::Result<bool>{
  if count<=0||count>1000||actor==to||item.is_empty()||item.len()>64||request.is_empty()||request.len()>128{return Ok(false)}
  let tx=self.db.transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)?;
  if tx.query_row("SELECT 1 FROM receipts WHERE id=?1 AND actor=?2",params![request,actor],|r|r.get::<_,i32>(0)).optional()?.is_some(){return Ok(false)}
  if tx.execute("UPDATE inventory SET quantity=quantity-?1 WHERE owner=?2 AND item=?3 AND quantity>=?1",params![count,actor,item])?!=1{return Ok(false)}
  tx.execute("INSERT INTO inventory VALUES(?1,?2,?3) ON CONFLICT(owner,item) DO UPDATE SET quantity=quantity+excluded.quantity",params![to,item,count])?;
  tx.execute("INSERT INTO receipts VALUES(?1,?2,'item transfer')",params![request,actor])?;tx.commit()?;Ok(true)
 }
 pub fn start_delivery(&self,actor:&str,job:&str)->rusqlite::Result<bool>{if job.is_empty()||job.len()>64{return Ok(false)}Ok(self.db.execute("INSERT OR IGNORE INTO jobs(id,owner) VALUES(?1,?2)",params![job,actor])?==1)}
 // Caller must supply a position independently validated by the server's simulation/telemetry.
 // Reward and destination are server constants, never arguments supplied by a client.
 pub fn finish_delivery(&mut self,actor:&str,job:&str,verified_position:[f32;3])->rusqlite::Result<bool>{
  if verified_position.iter().any(|v|!v.is_finite()){return Ok(false)}
  let target=[215.0_f32,-915.0,30.6];
  if verified_position.iter().zip(target).map(|(a,b)|(*a-b)*(*a-b)).sum::<f32>()>100.0{return Ok(false)}
  let tx=self.db.transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)?;
  if tx.execute("UPDATE jobs SET completed=1 WHERE id=?1 AND owner=?2 AND completed=0",params![job,actor])?!=1{return Ok(false)}
  if tx.execute("UPDATE characters SET cash=cash+100 WHERE id=?1 AND cash<=8999999999999900",[actor])?!=1{return Ok(false)}tx.commit()?;Ok(true)
 }
}
#[cfg(test)]mod tests{
 use super::*;
 fn core()->Core{let c=Core::open(":memory:").unwrap();c.create_character("alice","Alice").unwrap();c.create_character("bob","Bob").unwrap();c}
 #[test]fn deposit_cannot_mint_or_overdraw(){let mut c=core();assert!(!c.deposit("alice",-1,"x").unwrap());assert!(!c.deposit("alice",1,"x").unwrap());c.admin_grant("alice",100).unwrap();assert!(c.deposit("alice",80,"a").unwrap());assert!(!c.deposit("alice",80,"a").unwrap());assert!(!c.deposit("alice",30,"b").unwrap());assert_eq!(c.balance("alice").unwrap(),Some((20,80)));}
 #[test]fn inventory_transfer_is_atomic_and_idempotent(){let mut c=core();c.db.execute("INSERT INTO inventory VALUES('alice','water',5)",[]).unwrap();assert!(c.transfer_item("alice","bob","water",3,"tx").unwrap());assert!(!c.transfer_item("alice","bob","water",3,"tx").unwrap());assert!(!c.transfer_item("alice","bob","water",3,"tx2").unwrap());assert_eq!(c.db.query_row("SELECT sum(quantity) FROM inventory",[],|r|r.get::<_,i64>(0)).unwrap(),5);}
 #[test]fn inventory_failure_rolls_back_debit(){let mut c=core();c.db.execute("INSERT INTO inventory VALUES('alice','water',5)",[]).unwrap();assert!(c.transfer_item("alice","missing","water",3,"x").is_err());assert_eq!(c.db.query_row("SELECT quantity FROM inventory WHERE owner='alice'",[],|r|r.get::<_,i64>(0)).unwrap(),5);}
 #[test]fn job_owner_location_and_replay_checked(){let mut c=core();c.start_delivery("alice","job1").unwrap();assert!(!c.finish_delivery("bob","job1",[215.,-915.,30.6]).unwrap());assert!(!c.finish_delivery("alice","job1",[0.,0.,0.]).unwrap());assert!(c.finish_delivery("alice","job1",[215.,-915.,30.6]).unwrap());assert!(!c.finish_delivery("alice","job1",[215.,-915.,30.6]).unwrap());assert_eq!(c.balance("alice").unwrap(),Some((100,0)));}
 #[test]fn persistence_survives_reopen(){let p=std::env::temp_dir().join(format!("mugoat-rp-test-{}.sqlite",std::process::id()));{let c=Core::open(p.to_str().unwrap()).unwrap();c.create_character("alice","Alice").unwrap();c.admin_grant("alice",50).unwrap();}{let c=Core::open(p.to_str().unwrap()).unwrap();assert_eq!(c.balance("alice").unwrap(),Some((50,0)));}let _=std::fs::remove_file(p);}

 #[test]fn concurrent_deposits_cannot_double_spend(){
  use std::sync::{Arc,Barrier};
  let path=std::env::temp_dir().join(format!("mugoat-concurrency-{}.sqlite",std::process::id()));
  {let c=Core::open(path.to_str().unwrap()).unwrap();c.create_character("alice","Alice").unwrap();c.admin_grant("alice",100).unwrap();}
  let barrier=Arc::new(Barrier::new(2));
  let tasks:Vec<_>=(0..2).map(|n|{let p=path.clone();let b=barrier.clone();std::thread::spawn(move||{let mut c=Core::open(p.to_str().unwrap()).unwrap();b.wait();c.deposit("alice",70,&format!("concurrent-{n}")).unwrap()})}).collect();
  let successes=tasks.into_iter().filter_map(|t|t.join().ok()).filter(|ok|*ok).count();assert_eq!(successes,1);
  {let c=Core::open(path.to_str().unwrap()).unwrap();assert_eq!(c.balance("alice").unwrap(),Some((30,70)));}
  let _=std::fs::remove_file(path);
 }
}
