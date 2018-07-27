import React, { Component } from 'react'


export class DropDown extends Component {

    constructor(props) {
	super(props)
	this.state = {}
    }

    render() {
	return (
	    <div>
	    
	    <label style={this.props.labelStyle}>{this.props.label}</label>
	    <select style={this.props.dropDownStyle}
	    onChange={(e) => {this.props.onChange(e.target.value)}}
	    defaultValue={this.state.maskLabel}>

	    {this.props.options.map(function(option, index) {
		return (
		    <option value={index} key={index}>
		    {option}
		    </option>
		)
	    }.bind(this))}

	    </select>
	    
	    </div>
	)
    }
    
}

export class RadioButton extends Component {

    constructor(props) {
	super(props)
	this.state = {}
    }

    triggerOnClick() {
	this.props.onClick(this.props.val)
    }

    render() {
	return (
	    <div style={this.props.divStyle}>
	    <input style={this.props.radioStyle} type="radio"
	    onClick={this.triggerOnClick.bind(this)}
	    checked={this.props.checked ? "checked" : false}></input>
	    <p style={this.props.labelStyle}>{this.props.label}</p>
	    </div>
	)
    }
}

export class RadioList extends Component {

    constructor(props) {
	super(props)
    }

    onChange(index) {
	if (this.props.exclusionary === true) {
	    this.props.onChange(index)
	}
	else {
	    var checked = []
	    for (var i = 0; i < this.props.checked.length; i++) {
		if (i === index) {
		    checked.push(!(this.props.checked[index]))
		}
		else {
		    checked.push(this.props.checked[i])
		}
	    }
	    this.props.onChange(checked)
	}
    }

    render() {
	if (this.props.exclusionary === true) {
	    var checked = []
	    for (var i = 0; i < this.props.options.length; i++) {
		if (i === this.props.checked) {
		    checked.push(true)
		}
		else {
		    checked.push(false)
		}
	    }
	}
	else {
	    var checked = this.props.checked
	}
	
	return (
		<div style={this.props.divStyleOuter}>
		{this.props.options.map(function(label, index) {
		return (
		    <RadioButton label={label} val={index} onClick={this.onChange.bind(this)}
		    checked={checked[index]}
		    key={index}
		    labelStyle={this.props.labelStyle}
		    divStyle={this.props.divStyleInner} radioStyle={this.props.radioStyle} />
		)
	    }.bind(this))}
	    </div>
	)

    }
}
