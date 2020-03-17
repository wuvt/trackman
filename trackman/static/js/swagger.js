window.onload = function() {

    

    // Build a system
    const ui = SwaggerUIBundle(
    Object.assign(
    {

    url: "/api/spec.json",
    dom_id: '#swagger-ui',
    validatorUrl: null,
    deepLinking: true,
    jsonEditor: true,
    
    apisSorter: "alpha",
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
    ],
    plugins: [
        SwaggerUIBundle.plugins.DownloadUrl
    ],
    
    layout: "StandaloneLayout",
    
    },
    {}
    
    )
    
    )

    window.ui = ui

    //$(".topbar-wrapper .link span").replaceWith("<span>Flasgger</span>");
}
