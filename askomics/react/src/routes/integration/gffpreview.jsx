import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class GffPreview extends Component {
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      availableEntities: props.file.data.entities,
      entitiesToIntegrate: new Set(),
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      public: event.target.value == 'public',
      type: 'gff/gff3'
    }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          [tick]: true
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  handleSelection (event) {
    // console.log("value", event.target.value)
    // console.log(event)

    let value = event.target.value

    console.log("deal with", value)
    console.log(this.state.entitiesToIntegrate)


    if (!this.state.entitiesToIntegrate.has(value)) {
      this.setState({
        entitiesToIntegrate: new Set([...this.state.entitiesToIntegrate]).add(value)
      })
    }else {
      this.setState({
        entitiesToIntegrate: new Set([...this.state.entitiesToIntegrate]).delete(value)
      })
    }

    console.log(this.state.entitiesToIntegrate)



  }





  render () {

    let privateIcon = <i className="fas fa-lock"></i>
    if (this.state.privateTick) {
      privateIcon = <i className="fas fa-check text-success"></i>
    }
    let publicIcon = <i className="fas fa-globe-europe"></i>
    if (this.state.publicTick) {
      publicIcon = <i className="fas fa-check text-success"></i>
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <br />
            <div>
              <FormGroup check>
                {this.state.availableEntities.map(entity => {
                  return (<p><Input value={entity} onClick={this.handleSelection} type="checkbox" /> {entity}</p>)
                })}
              </FormGroup>
            </div>
          <br />
          <ButtonGroup>
            <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
            <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
          </ButtonGroup>
      </div>
    )
  }
}
