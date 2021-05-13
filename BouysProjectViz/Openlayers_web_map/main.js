window.onload = init;

function init() {
    var map = new ol.Map({
        //controls: defaultControls().extend([RotateNorthControl()]),
        target: 'map',
        layers: [
        new ol.layer.Tile({
            source: new ol.source.Stamen({layer: 'terrain'})
          }),
        new ol.layer.Tile({
            source: new ol.source.Stamen({layer: 'terrain-labels'})
        })
        ],
        view: new ol.View({
          center: ol.proj.fromLonLat([37.41, 8.82]),
          zoom: 4,
          rotation: .5
        })
    });


    const strokeStyle = new ol.style.Stroke ({
        color: [46, 45, 45, 1],
        width: 1.2
    })

    const circleStyle = new ol.style.Circle({
        fill: new ol.style.Fill({
            color: [245, 49, 5, 1]
        }),
        radius: 7,
        stroke: strokeStyle
    })

    //Compass Layer
    

    //Vector Layer
    const testBouy = new ol.layer.VectorImage({
        source: new ol.source.Vector({
            url: './data/testBouyData.geoJSON',
            format: new ol.format.GeoJSON()
        }),
        visible: true,
        title: 'Test Bouy',
        style: new ol.style.Style({
            stroke: strokeStyle,
            image: circleStyle
        })
    })

    map.addLayer(testBouy);

    //Clicking reveals info
    const overlayContainerElement = document.querySelector('.overlay-container');
    const overlayLayer = new ol.Overlay({
        element: overlayContainerElement
    })
    map.addOverlay(overlayLayer)
    const overlayFeatureIMEI = document.getElementById('Feature-IMEI');
    const overlayFeatureTs = document.getElementById('Feature-Ts');
    const overlayFeatureBP = document.getElementById('Feature-BP');


    map.on('click', function(e){
        overlayLayer.setPosition(undefined);
        map.forEachFeatureAtPixel(e.pixel, function(feature, layer){
            
            let clickedCoord = e.coordinate;
            let clickedIMEI = feature.get('IMEI');
            let clickedTs = feature.get('Ts');
            let clickedBP = feature.get('BP');
            overlayLayer.setPosition(clickedCoord);
            overlayFeatureIMEI.innerHTML = clickedIMEI;
            overlayFeatureTs.innerHTML = clickedTs;
            overlayFeatureBP.innerHTML = clickedBP;
        })
    })



}