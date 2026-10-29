"""1.5.1-compatible fallback for the unmapped scaled-look axes, not mission bypasses."""
def axis_fallback(function):
 return (f'  if ((var_p1 == 290u || var_p1 == 291u) && value == 0.0f)\n'
         f'    value = pg_control_original_f{function}(instance, var_p0, var_p1 == 290u ? 1u : 2u); /* scaled-look fallback */\n')
def script_fallback(function,memory):
 return (f'  {{ /* scaled-look fallback for inlined script native */\n'
         f'    u32 control = i32_load_shared({memory}(u64)(args));\n'
         f'    u32 action = i32_load_shared({memory}(u64)checked_add_u64(args, 8u));\n'
         f'    f32 value = f32_load_shared({memory}(u64)(answer));\n'
         f'    if ((action == 290u || action == 291u) && value == 0.0f) {{\n'
         f'      extern f32 w2c_game_f{function}(w2c_game*, u32, u32);\n'
         f'      value = w2c_game_f{function}(instance, control, action == 290u ? 1u : 2u);\n'
         f'      f32_store_shared({memory}(u64)(answer), value);\n'
         f'    }}\n  }}\n')
