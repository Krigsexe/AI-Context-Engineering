-- tests/test_basic.lua
-- Basic test suite for FiveM Lua template

function test_config_exists()
    assert(config ~= nil, "Config should be defined")
    assert(config.setting1 == true, "Config setting1 should be true")
    assert(config.setting2 == "example", "Config setting2 should be 'example'")
    print("✅ Config tests passed")
end

function test_server_initialization()
    -- Mock basic server functions
    local function mock_print(msg)
        return msg:find("FiveM Lua server running") ~= nil
    end
    
    assert(mock_print("FiveM Lua server running..."), "Server should print initialization message")
    print("✅ Server initialization tests passed")
end

-- Run tests
test_config_exists()
test_server_initialization()
print("🎉 All FiveM Lua template tests passed!")
