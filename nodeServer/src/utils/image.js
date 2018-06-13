function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}


export class Image {
    
    constructor(data, pixHeight, pixWidth) {
	this.data = data
	this.pixHeight = pixHeight
	this.pixWidth = pixWidth
	this.scale = 1
	this.mask = []
	for (var i = 0; i < data.length; i++) {
	    this.mask.push([])
	    for (var j = 0 ; j < data[0].length; j++) {
		this.mask[i].push(0)
	    }
	}
	this.maskColours = ["#FFFFFF"]
    }

    drawImage(canvas, level, window) {
	console.log("draw")
	// Get the dimensions
	var height = this.data.length
	var width  = this.data[0].length
	var pixHeight = this.pixHeight
	var pixWidth = this.pixWidth
	
	// Height of the canvas is always 400
	var size   = 400
	var actualSize = height*pixHeight
	
	// Size the canvas correctly
	var scale = size/actualSize
	this.scale = scale
	canvas.height = size
	canvas.width  = width * pixWidth * scale
	
	// Clear the canvas
	var ctx = canvas.getContext("2d")
	ctx.clearRect(0, 0, width*scale, height*scale);
	
	// Draw the image onto the canvas
	for (var row = 0; row < height; row++) {
	    for (var col = 0; col < width; col++) { 
		var grayVal = parseInt(this.data[row][col])
		// Transfer function
		if (grayVal < level - window/2) {
		    grayVal = 0
		}
		else if (grayVal > level + window/2) {
		    grayVal = 255
		}
		else {
		    grayVal = (grayVal - (level - window/2))*255/window
		}
		grayVal = Math.round(grayVal)
		ctx.fillStyle = rgbToHex(grayVal, grayVal, grayVal); // Set the color to the one specified
		ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(pixHeight*scale)); // Actually draw the rectangle

		if (this.mask[row][col] !== 0) {
		    ctx.fillStyle = this.maskColours[this.mask[row][col] - 1]; // Set the color to the one specified
		    ctx.fillRect(Math.floor(col * pixWidth * scale), Math.floor(row * pixHeight*scale), Math.ceil(pixWidth*scale), Math.ceil(pixHeight*scale));
		}
	    }
	}
    }

    addToMask(x, y, val) {
	var col = Math.floor(x / (this.pixWidth * this.scale))
	var row = Math.floor(y / (this.pixHeight * this.scale))
	this.mask[row][col] = val
    }
    
}
