import {Image} from "./image.js"

// Holds the 2D images and provides method for altering each of the views
export class Image3D {
    
    constructor(dataX, pixHeight, pixWidth, pixDepth) {
	this.nImages = dataX.length
	this.height  = dataX[0].length
	this.width   = dataX[0][0].length
	this.imagesX = this.imgArray(this.nImages, this.height, this.width, pixHeight, pixWidth)
	this.imagesY = this.imgArray(this.width, this.nImages, this.height, pixDepth, pixWidth)
	this.imagesZ = this.imgArray(this.height, this.nImages, this.width, pixDepth, pixHeight)
	this.pixHeight = pixHeight
	this.pixWidth  = pixWidth
	this.pixDepth  = pixDepth
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    for (var y = 0; y < this.height; y++) {
		for (var x = 0; x < this.width; x++) {
		    //if (this.nImages !== 10) {console.log(nImg, y, x, this.imagesY)}
		    this.setPixel(nImg, y, x, dataX[nImg][y][x])
		}
	    }
	}
	this.boundingRect = [0,0,0,this.nImages,this.height,this.width] // (x1,y1,z1), (x2,y2,z2)
	this.setBoundingRect(0,0,0,this.boundingRect[3],this.boundingRect[4],this.boundingRect[5])
	this.setupEvents()
    }

    // Build an array of images
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

    getImgArr() {
	var currImg = this
	var imgArr = []
	for (var i = 0; i < currImg.nImages; i++) {
	    imgArr.push([])
	    for (var j = 0; j < currImg.height; j++) {
		imgArr[i].push([])
		for (var k = 0; k < currImg.width; k++) {
		    imgArr[i][j].push(currImg.imagesX[i].data[j][k])
		}
	    }
	}
	return imgArr
    }

    // Return the 3D mask array 
    getMaskArr(maskIndex) {
	var currImg = this
	var labelArr = []
	for (var i = 0; i < currImg.nImages; i++) {
	    labelArr.push([])
	    for (var j = 0; j < currImg.height; j++) {
		labelArr[i].push([])
		for (var k = 0; k < currImg.width; k++) {
		    labelArr[i][j].push(currImg.imagesX[i].masks[maskIndex][j][k])
		}
	    }
	}
	return labelArr
    }

    getNumMasks() {
	return this.imagesX[0].masks.length
    }

    addNewMask(mask) {
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

    // Set up events on the 2D images in order to update the 3D image when a change is made
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

    // Set a pixel value in all 3 axis
    setPixel(nImg, row, col, val) {
	this.imagesX[nImg].data[row][col] = val
	this.imagesY[col].data[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].data[(this.nImages-1) - nImg][col] = val
    }

    // Set a mask value in all 3 axis
    setMask(nImg, row, col, val, mask) {
	this.imagesX[nImg].masks[mask][row][col] = val
	this.imagesY[col].masks[mask][(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].masks[mask][(this.nImages-1) - nImg][col] = val
	this.imagesX[nImg].tempMask[row][col] = val
	this.imagesY[col].tempMask[(this.nImages-1) - nImg][row] = val
	this.imagesZ[row].tempMask[(this.nImages-1) - nImg][col] = val
    }

    // Copy mask into maskIndeth mask
    copyMask(mask, maskIndex) {
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    for (var y = 0; y < this.height; y++) {
		for (var x = 0; x < this.width; x++) {
		    this.setMask(nImg, y, x, mask[nImg][y][x], maskIndex)
		}
	    }
	}
    }

    // Set the edges of the bounding rectanle
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

    // Produce an image that is a cropped version of the original
    cropToBoundingRect() {
	var img1 = (this.nImages) - this.boundingRect[0]
	var img2 = (this.nImages) - this.boundingRect[3]
	var row1 = this.boundingRect[2]
	var row2 = this.boundingRect[5]
	var col1 = this.boundingRect[1]
	var col2 = this.boundingRect[4]
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
	var data = []
	// Loop, only adding those in cropped region
	for (var img = img1; img < img2; img++) {
	    data.push([])
	    for (var row = row1; row < row2; row++) {
		data[img - img1].push([])
		for (var col = col1; col < col2; col++) {
		    data[img - img1][row - row1].push(this.imagesX[img].data[row][col])
		}
	    }
	}
	var croppedImg = new Image3D(data, this.pixHeight, this.pixWidth, this.pixDepth)
	var masks = []
	// Transfer masks over
	for (var i = 0; i < this.imagesX[0].masks.length; i++) {
	    if (i > 0) {
		croppedImg.addNewMask()
	    }
	    for (var img = img1; img < img2; img++) {
		for (var row = row1; row < row2; row++) {
		    for (var col = col1; col < col2; col++) {
			croppedImg.setMask(img - img1, row - row1,
					   col - col1,
					   this.imagesX[img].masks[i][row][col], i)
		    }
		}
	    }
	}
	return croppedImg
    }

    calculateDice(mask1, mask2) {
	var total = 0
	var count = 0
	for (var nImg = 0; nImg < this.nImages; nImg++) {
	    for (var y = 0; y < this.height; y++) {
		for (var x = 0; x < this.width; x++) {
		    var val1 = this.imagesX[nImg].masks[mask1][y][x]
		    var val2 = this.imagesX[nImg].masks[mask2][y][x] 
		    if (val1 === 1) {
			total += 1
		    }
		    if (val2 === 1) {
			total += 1
			if (val1 === val2) {
			    count += 2
			}
		    }
		}
	    }
	}
	return count/total
    }
    
}
