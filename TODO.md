# TODO: Fix Issues in flux_backend.py

- [x] Step 1: Fix uninitialized `optimization_advice` in `allocate_floating_memory` by adding default value
- [ ] Step 2: Reorder functions: Move `create_flux_connection` before `execute_flux_program` for clarity
- [ ] Step 3: Enhance error handling in WebSocket handlers with specific exception logging
- [ ] Step 4: Add size limit for FLUX code blocks in parsing to prevent regex timeouts
- [ ] Step 5: Implement cleanup in `handle_disconnect` for connections and memory
