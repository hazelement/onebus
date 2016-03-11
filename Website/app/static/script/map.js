
var map;
var infowindow;
var home;
var directionsDisplay;
var directionsService;
var markers = [];
var shapes = []
var home_gps;
//var myIcon = new google.maps.MarkerImage(
//    "/static/images/my_location.png",
//    null, /* size is determined at runtime */
//    null, /* origin is 0,0 */
//    null, /* anchor is bottom center of the scaled image */
//    new google.maps.Size(42, 68)
//);

//
//var myIcon={
//  url: "/static/images/my_location.png",
//  size: new google.maps.Size(71, 71),
//  origin: new google.maps.Point(0, 0),
//  anchor: new google.maps.Point(17, 34),
//  scaledSize: new google.maps.Size(25, 25)
//};
// todo use jQuery AJAX to post current address and a lot of locations to server, server to filter for locations along bus stops get targeted locations
// http://www.w3schools.com/jquery/jquery_ajax_get_post.asp

// todo https://chadkillingsworth.github.io/geolocation-marker/   detect location of user

function initMap(){
    var mapDiv = document.getElementById('map');

    map = new google.maps.Map(mapDiv, {
        zoom: 12,
    });

    var geo_options = {
        enableHighAccuracy: true,
        maximumAge        : 30000,
        timeout           : 1000
    };

// todo figure out this GPS data
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(location_success, location_error, geo_options);
    } else {
        home_gps = {lat: 51.0486151, lng:-114.0708459}
        map.setCenter(home_gps)
    }

    directionsDisplay = new google.maps.DirectionsRenderer;
    directionsService = new google.maps.DirectionsService;
    infowindow = new google.maps.InfoWindow({
        content: '',
        maxWidth: 200
        });

     google.maps.event.addListener(
        map,
        'click',
        function(){
                infowindow.close();
//                directionsDisplay.setMap(null);
        }
    );

        // setup map
    directionsDisplay.setMap(map);
    directionsDisplay.setOptions( { suppressMarkers: true } );
//    directionsDisplay.setPanel(document.getElementById('direction-panel'));

}

function location_success(position) {
    home_gps = {lat: position.coords.latitude, lng: position.coords.longitude};
    map.setCenter(home_gps)
}

function location_error() {
    home_gps = {lat: 51.0486151, lng:-114.0708459}
    map.setCenter(home_gps)
}

function refreshMap(data) {

    // define map elements
    destinations = data['results']

    map.setCenter({lat: home_gps.lat, lng:home_gps.lng})

    // add home marker
    add_marker(home_gps, true);

    // add result markers
    for( var key in destinations ){
        add_marker(destinations[key], false);
    }

//    add_shape(data['shape']);

}

//function add_shape(shape_gps){
//
//    var shape = new google.maps.Polyline({
//        path: shape_gps,
//        geodesic: true,
//        strokeColor: '#ff4d4d ',
//        strokeOpacity: 0.7,
//        strokeWeight: 4
//    });
//
//    shape.setMap(map);  // add loop to load multiple shapes
//    shapes.push(shape);
//
//}

function add_marker(target, is_home) {
    var lat_lng = {lat: target.lat, lng: target.lng};
    if(is_home){

        var marker = new google.maps.Marker({
        position: lat_lng,
        labelContent: 'H',
        map: map,
        animation: google.maps.Animation.DROP,
        title: 'Home',
        description: 'Home Location',
        path: target.path
        });
//        marker.setIcon(myIcon);
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');

        google.maps.event.addListener(
            marker,
            'click',
            function(){
                infowindow.close();
                infowindow.setContent(marker.description);
                infowindow.open(map, marker);
            }
        );
        markers.push(marker);

    } else {

        var marker = new google.maps.Marker({
        position: lat_lng,
        map: map,
        animation: google.maps.Animation.DROP,
        title: target.dest_name,
        description: target.address,
        path: target.path
        });

        google.maps.event.addListener(
            marker,
            'click',
            function(){
                infowindow.close();
                infowindow.setContent(target.dest_name + "\n" +marker.description);
                infowindow.open(map, marker);
                directionsDisplay.setMap(map)
                calculateAndDisplayRoute(marker);
//                document.getElementById("direction-panel-background").style.backgroundColor='white'

            }
        );
        markers.push(marker);
    }

}

function calculateAndDisplayRoute(dest) {
  var selectedMode = 'TRANSIT';
  directionsService.route({
    origin: {lat: home_gps.lat, lng: home_gps.lng},  // Haight.
    destination: {lat: dest.position.lat(), lng: dest.position.lng()},  // Ocean Beach.
    // Note that Javascript allows us to access the constant
    // using square brackets and a string value as its
    // "property."
    travelMode: google.maps.TravelMode[selectedMode],
     transitOptions: {
    modes: [google.maps.TransitMode.BUS],
    routingPreference: google.maps.TransitRoutePreference.FEWER_TRANSFERS
    },
  }, function(response, status) {
    if (status == google.maps.DirectionsStatus.OK) {

      directionsDisplay.setDirections(response);
    } else {
      window.alert('Directions request failed due to ' + status);
    }
  });
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Removes the markers from the map, but keeps them in the array.
//function clearMarkers() {
//  setMapOnAll(null);
//  deleteMarkers(); // clear all old markers
//}


// Deletes all markers and bus routes in the array by removing references to them.
function clearMap() {
  setMapOnAll(null);
//  clearMarkers();
  markers = [];
  directionsDisplay.setMap(null);

}