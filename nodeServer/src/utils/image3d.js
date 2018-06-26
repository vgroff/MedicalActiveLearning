import {Image} from "./image.js"

export class Image3D {
    
    constructor(dataX, pixHeight, pixWidth, pixDepth) {
	this.nImages = dataX.length
	this.height  = dataX[0].length
	this.width   = dataX[0][0].length
	this.imagesX = this.imgArray(this.nImages, this.height, this.width, pixHeight, pixWidth)
	this.imagesY = this.imgArray(this.height, this.nImages, this.width, pixDepth, pixWidth)
	this.imagesZ = this.imgArray(this.width, this.nImages, this.height, pixDepth, pixHeight)
	this.pixHeight = pixHeight
	this.pixWidth  = pixWidth
	this.pixDepth  = pixDepth
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    for (var y = 0; y < this.height; y++) {
		for (var x = 0; x < this.width; x++) {
		    this.setPixel(nImg, y, x, dataX[nImg][y][x])
		}
	    }
	}
	this.boundingRect = [0,0,0,0,0] // (x1,y1,z1), (x2,y2,z2)
	this.setupEvents()
    }

    imgArray(nImages, height, width, pixHeight, pixWidth) {
	var images = []
	for (var nImg = 0; nImg < nImages; nImg++) {
	    var data = []
	    for (var y = 0; y < height; y++) {
		data.push([])
		for (var x = 0; x < width; x++) {
		    data[y].push(0)
		}
	    }
	    var img = new Image(data, pixHeight, pixWidth)
	    images.push(img)
	}
	return images
    }

    setupEvents() {
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    var img = this.imagesX[nImg]
	    var f = function(nImage, row, col, val) {
		this.setMask(nImage, row, col, val)
	    }.bind(this, nImg)
	    img.addEvent("maskChange", f)
	}
	for (var col = 0; col < this.width; col++) {
	    var img = this.imagesY[col]
	    var f = function(column, invNImg, row, val) {
		this.setMask((this.nImages-1)-invNImg, row, column, val)
	    }.bind(this, col)
	    img.addEvent("maskChange", f)
	}
	for (var row = 0; row < this.height; row++) {
	    var img = this.imagesZ[row]
	    var f = function(r, invNImg, col, val) {
		this.setMask((this.nImages-1)-invNImg, r, col, val)
	    }.bind(this, row)
	    img.addEvent("maskChange", f)
	}
    }

    setPixel(nImg, row, col, val) {
	this.imagesX[nImg].data[row][col] = val
	this.imagesY[col].data[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].data[(this.nImages-1) - nImg][col] = val
    }

    setMask(nImg, row, col, val) {
	this.imagesX[nImg].mask[row][col] = val
	this.imagesY[col].mask[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].mask[(this.nImages-1) - nImg][col] = val
	this.imagesX[nImg].tempMask[row][col] = val
	this.imagesY[col].tempMask[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].tempMask[(this.nImages-1) - nImg][col] = val
    }
    
}
