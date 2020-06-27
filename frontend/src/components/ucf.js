import React from 'react'
import PropTypes from 'prop-types'

const UCFFile = ({ onClick, completed, text }) => (
  <li
    onClick={onClick}
    style={{
      textDecoration: completed ? 'line-through' : 'none'
    }}
  >
    {text}
  </li>
)


// In a more sustainable/longer running application I would probably look at
// modeling the data more cleanly.

// I'm making some assumptions via my own previous lab work about what is
// and isn't important in the context of optimization. I could be wrong.
UCFFile.propTypes = {
  version: PropTypes.string.isRequired,
  organism: PropTypes.string.isRequired,

  completed: PropTypes.bool.isRequired,
  text: PropTypes.string.isRequired
}

export default UCFFile