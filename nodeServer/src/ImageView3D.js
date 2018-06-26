import React, { Component } from 'react'
import {ImageView2D} from "./ImageView2D.js"


export class ImageView3D extends Component {

    constructor(props) {
	super(props)
	this.props = props
	console.log(this.props)
	this.state = {}
    }

    drawAll() {
	this.refs.imgX.drawImage()
	this.refs.imgY.drawImage()
	this.refs.imgZ.drawImage()
    }

    render() {
	if (this.props.image) {
	    console.log("Drawing 3d")
	    
	    return (
		<div>
		
		<ImageView2D ref="imgX" images = {this.props.image.imagesX}
		level = {this.props.level} window = {this.props.window}
		brushSize={this.props.brushSize} 
		maskColours = {this.props.maskColours} maskLabel={this.props.maskLabel}
		action={this.props.action} onChange={this.drawAll.bind(this)}/>

		<ImageView2D ref="imgY" images = {this.props.image.imagesY}
		level = {this.props.level}
		window = {this.props.window} brushSize={this.props.brushSize}
		maskColours = {this.props.maskColours} maskLabel={this.props.maskLabel}
		action={this.props.action} onChange={this.drawAll.bind(this)}/>

		<ImageView2D ref="imgZ" images = {this.props.image.imagesZ}
		level = {this.props.level}
		window = {this.props.window} brushSize={this.props.brushSize}
		maskColours = {this.props.maskColours} maskLabel={this.props.maskLabel}
		action={this.props.action} onChange={this.drawAll.bind(this)}/>

		</div>
	    )
	}
	else {
	    return (<div></div>)
	}
    }
}
