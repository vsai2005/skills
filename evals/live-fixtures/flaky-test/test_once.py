from shared_resource import acquire_port

if not acquire_port():
    print("FAIL: fixed port already owned")
    raise SystemExit(1)
print("PASS")
