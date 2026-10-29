#include "GameInstallerShim.h"
#include <stdbool.h>
bool PGModFileProblem(const char *,char *,size_t);

#include <stdint.h>
#include <stdbool.h>
void PGEnableSoundMods(bool enabled);
bool PGRegisterStockVehicleSound(uint32_t model,const char *profile);
bool PGSelectVehicleSound(uint32_t model,const char *profile);
