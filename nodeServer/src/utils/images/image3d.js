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
	this.boundingRect = [0,0,0,this.nImages,this.width,this.height] // (x1,y1,z1), (x2,y2,z2)
	this.setBoundingRect(0,0,0,this.boundingRect[3],this.boundingRect[4],this.boundingRect[5])
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

    getNumMasks() {
	return this.imagesX[0].masks.length
    }

    addNewMask() {
	for (var nImg = 0; nImg < this.imagesX.length; nImg++) {
	    this.imagesX[nImg].addNewMask()
	}
	for (var nImg = 0; nImg < this.imagesY.length; nImg++) {
	    this.imagesY[nImg].addNewMask()
	}
	for (var nImg = 0; nImg < this.imagesZ.length; nImg++) {
	    this.imagesZ[nImg].addNewMask()
	}
    }

    setActiveMask(maskIndex) {
	for (var nImg = 0; nImg < this.imagesX.length; nImg++) {
	    this.imagesX[nImg].setActiveMask(maskIndex)
	}
	for (var nImg = 0; nImg < this.imagesY.length; nImg++) {
	    this.imagesY[nImg].setActiveMask(maskIndex)
	}
	for (var nImg = 0; nImg < this.imagesZ.length; nImg++) {
	    this.imagesZ[nImg].setActiveMask(maskIndex)
	}
    }

    setupEvents() {
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    var img = this.imagesX[nImg]
	    var f = function(nImage, row, col, val, mask) {
		this.setMask(nImage, row, col, val, mask)
	    }.bind(this, nImg)
	    img.addEvent("maskChange", f)
	    var f = function(boundingRect) {
		this.setBoundingRect(this.boundingRect[0], boundingRect[1],
				     boundingRect[0], this.boundingRect[3],
				     boundingRect[3], boundingRect[2])
	    }.bind(this)
	    img.addEvent("rectChange", f)
	}
	for (var col = 0; col < this.width; col++) {
	    var img = this.imagesY[col]
	    var f = function(column, invNImg, row, val, mask) {
		this.setMask((this.nImages-1)-invNImg, row, column, val, mask)
	    }.bind(this, col)
	    img.addEvent("maskChange", f)
	    var f = function(boundingRect) {
		this.setBoundingRect(boundingRect[1], boundingRect[0],
				     this.boundingRect[1], boundingRect[3],
				     boundingRect[2], this.boundingRect[4])
	    }.bind(this)
	    img.addEvent("rectChange", f)
	}
	for (var row = 0; row < this.height; row++) {
	    var img = this.imagesZ[row]
	    var f = function(r, invNImg, col, val, mask) {
		this.setMask((this.nImages-1)-invNImg, r, col, val, mask)
	    }.bind(this, row)
	    img.addEvent("maskChange", f)
	    var f = function(boundingRect) {
		this.setBoundingRect(boundingRect[1], this.boundingRect[2],
				     boundingRect[0], boundingRect[3],
				     this.boundingRect[5], boundingRect[2])
	    }.bind(this)
	    img.addEvent("rectChange", f)
	}
    }

    setPixel(nImg, row, col, val) {
	this.imagesX[nImg].data[row][col] = val
	this.imagesY[col].data[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].data[(this.nImages-1) - nImg][col] = val
    }

    setMask(nImg, row, col, val, mask) {
	this.imagesX[nImg].masks[mask][row][col] = val
	this.imagesY[col].masks[mask][(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].masks[mask][(this.nImages-1) - nImg][col] = val
	this.imagesX[nImg].tempMask[row][col] = val
	this.imagesY[col].tempMask[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].tempMask[(this.nImages-1) - nImg][col] = val
    }

    setBoundingRect(nImg1, row1, col1, nImg2, row2, col2) {
	this.boundingRect = [nImg1, col1, row1, nImg2, col2, row2]
	var img1 = (this.nImages) - nImg1
	var img2 = (this.nImages) - nImg2
	var temp
	if (img1 > img2) {
	    temp = img1
	    img1 = img2
	    img2 = temp
	}
	if (row1 > row2) {
	    temp = row1
	    row1 = row2
	    row2 = temp
	}
	if (col1 > col2) {
	    temp = col1
	    col1 = col2
	    col2 = temp
	}
	for (var img = 0; img < this.nImages; img++) {
	    if (img >= img1 && img < img2) {
		this.imagesX[img].setRectPix(row1, col1, row2, col2)
	    }
	    else {
		this.imagesX[img].setRectPix(0,0,0,0)
	    }
	}
	for (var col = 0; col < this.width; col++) {
	    if (col >= col1 && col < col2) {
		this.imagesY[col].setRectPix((this.nImages) - img2, row1,
					     (this.nImages) - img1, row2)
	    }
	    else {
		this.imagesY[col].setRectPix(0,0,0,0)
	    }
	}
	for (var row = 0; row < this.height; row++) {
	    if (row >= row1 && row < row2) {
		this.imagesZ[row].setRectPix((this.nImages) - img2, col1,
					     (this.nImages) - img1, col2)
	    }
	    else {
		this.imagesZ[row].setRectPix(0,0,0,0)
	    }
	}
    }

    cropToBoundingRect() {
	var data = []
	for (var img = this.boundingRect[0]; img < this.boundingRect[3]; img++) {
	    data.push([])
	    for (var row = this.boundingRect[1]; row < this.boundingRect[4]; row++) {
		data.push([])
		for (var col = this.boundingRect[2]; col < this.boundingRect[5]; col++) {
		    data.push(this.imagesX[img].data[row][col])
		}
	    }
	}
	var croppedImg = new Image(data, this.pixHeight, this.pixWidth, this.pixDepth)
	var masks = []
	for (var i = 0; i < this.imagesX[0].masks.length; i++) {
	    if (i > 0) {
		croppedImg.addNewMask()
	    }
	    for (var img = this.boundingRect[0]; img < this.boundingRect[3]; img++) {
		for (var row = this.boundingRect[1]; row < this.boundingRect[4]; row++) {
		    for (var col = this.boundingRect[2]; col < this.boundingRect[5]; col++) {
			croppedImg.setMask(img - this.boundingRect[0], row - this.boundingRect[1],
					   col - this.boundingRect[2],
					   this.imagesX[img].masks[i][row][col], i)
		    }
		}
	    }
	}
	return croppedImg
    }
    
}
