#!/usr/bin/env node
var exec = require( 'child_process' ).exec;

var colorMap = [
    { threshold: 0,   color: { r: 0xFF, g: 0x00, b: 0x00 } },
    { threshold: 50,  color: { r: 0xFF, g: 0xFF, b: 0x00 } },
    { threshold: 100, color: { r: 0xFF, g: 0xFF, b: 0xFF } }
];

var toHex = function( value ) {
    var hex = value.toString( 16 );
    return hex.length === 1 ? '0' + hex : hex;
};

exec( 'acpi -b', function( error, stdout ) {
    var percentage = +stdout.match( /(\d+)%/ )[1];
    var i;
    for( i = 1; i < colorMap.length - 1; i++ ) {
        if( percentage < colorMap[i].threshold ) {
            break;
        }
    }

    var lowerBound = colorMap[i-1],
        upperBound = colorMap[i],
        range = upperBound.threshold - lowerBound.threshold,
        rangePercentage = (percentage - lowerBound.threshold) / range,
        lowerPercentage = 1 - rangePercentage,
        upperPercentage = rangePercentage;

    var color = {
        r: Math.floor( lowerBound.color.r * lowerPercentage + upperBound.color.r * upperPercentage ),
        g: Math.floor( lowerBound.color.g * lowerPercentage + upperBound.color.g * upperPercentage ),
        b: Math.floor( lowerBound.color.b * lowerPercentage + upperBound.color.b * upperPercentage ),
};

    process.stdout.write( '#' + toHex( color.r ) + toHex( color.g ) + toHex( color.b ) );
} );
