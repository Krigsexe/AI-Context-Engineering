fx_version 'cerulean'
game 'gta5'

name 'ODIN Sample Resource'
author 'Make With Passion by Krigs'
version '6.0.0'
description 'Sample FiveM resource for testing ODIN v6.0 capabilities'

-- Server scripts
server_scripts {
    'server/main.lua',
    'server/database.lua',
    'server/events.lua',
    'server/commands.lua'
}

-- Client scripts
client_scripts {
    'client/main.lua',
    'client/events.lua',
    'client/ui.lua'
}

-- Shared scripts
shared_scripts {
    'shared/config.lua',
    'shared/utils.lua'
}

-- Files for download
files {
    'html/index.html',
    'html/script.js',
    'html/style.css'
}

-- NUI page
ui_page 'html/index.html'

-- Dependencies
dependencies {
    'mysql-async'
}

-- Export functions
exports {
    'GetPlayerData',
    'SetPlayerData',
    'SendNotification'
}

-- Server exports
server_exports {
    'SavePlayerData',
    'LoadPlayerData',
    'GetServerStats'
}
