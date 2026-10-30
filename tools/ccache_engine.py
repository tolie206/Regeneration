"""Cache generated C; remove ONLY inert module-session flags when -fno-modules wins."""
import os,sys,shlex,subprocess
from pathlib import Path

def expand(args,depth=0):
 if depth>8:raise ValueError('response nesting too deep')
 result=[]
 for arg in args:
  if arg.startswith('@') and Path(arg[1:]).is_file():result.extend(expand(shlex.split(Path(arg[1:]).read_text()),depth+1))
  else:result.append(arg)
 return result

def cache_args(args):
 expanded=expand(args)
 # Keep all original arguments for files whose module mode cannot be proven.
 mode=[a for a in expanded if a in ('-fmodules','-fno-modules')]
 if not mode or mode[-1]!='-fno-modules':return None
 single={'-fmodules','-fmodules-validate-once-per-build-session'}
 prefixes=('-fmodules-cache-path=','-fmodules-prune-interval=','-fmodules-prune-after=','-fbuild-session-file=','-fbuild-session-timestamp=')
 return [a for a in expanded if a not in single and not a.startswith(prefixes)]

def main():
 real=os.environ['PG_REAL_CLANG'];original=sys.argv[1:]
 try:args=cache_args(original)
 except (ValueError,OSError):args=None
 if args is None:return subprocess.call([real,*original])
 return subprocess.call(['ccache',real,*args])
if __name__=='__main__':sys.exit(main())
