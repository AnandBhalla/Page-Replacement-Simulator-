import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import MemorySimulation from './components/MemorySimulation.jsx'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <MemorySimulation/>
    </>
  )
}

export default App
