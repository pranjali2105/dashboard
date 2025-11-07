// Save this in your assets/ folder as theme_changer.js

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        dbc_themes: {
            dark: "https://cdnjs.cloudflare.com/ajax/libs/bootswatch/5.3.3/cyborg/bootstrap.min.css",
            light: "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css"
        },
        ag_themes: {
            dark: "https://cdn.jsdelivr.net/npm/ag-grid-community@31.1.1/styles/ag-theme-alpine-dark.css",
            light: "https://cdn.jsdelivr.net/npm/ag-grid-community@31.1.1/styles/ag-theme-alpine.css"
        },

        toggle_theme: function(theme) {
            
            if (!theme) {
                theme = 'dark';
            }

            var theme_data = {
                'dark': {
                    dbc: window.dash_clientside.clientside.dbc_themes.dark,
                    ag: window.dash_clientside.clientside.ag_themes.dark,
                    switch_val: true,
                    icon_class: 'bi bi-moon-fill text-light'
                },
                'light': {
                    dbc: window.dash_clientside.clientside.dbc_themes.light,
                    ag: window.dash_clientside.clientside.ag_themes.light,
                    switch_val: false,
                    icon_class: 'bi bi-sun-fill text-dark'
                }
            };
            
            var current_theme = theme_data[theme];

                current_theme.dbc,          
                current_theme.ag,           
                current_theme.switch_val,   
                current_theme.icon_class ;
        }
    }
});
