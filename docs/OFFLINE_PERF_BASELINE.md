# Evidence before V5R1
External E:/START V5R0 Logs(2).zip: 145 FPS samples over approximately 24m53s, overall mean 54.33, late GPU 18.7-19.5ms and 94-100% busy. This is another DXMT port, NOT a measured V5 native-Metal baseline. -metalfx=1.5 is an argument, not proof that scaling executed. Logs(1) contains only nine FPS samples. Missing cleanup log lines do not establish that no memory reclamation exists; no RAM protections were removed on this basis.

Local V5 device baseline: NOT MEASURED. Need R008 versus V5 same device/data/save/route/output height, starting temperature, no charging; 3 runs each. Preserve logs from startup through 20 minutes. CPU simulation/decode timings without instrumentation: NOT MEASURED.
