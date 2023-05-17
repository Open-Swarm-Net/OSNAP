import { ThemeProvider, createTheme } from '@mui/material'
import { Container } from '@mui/system'

const theme = createTheme({
  breakpoints: {
    values: {
      xxs: 0, // small phone
      xs: 300, // phone
      sm: 600, // tablets
      md: 900, // small laptop
      lg: 1200, // desktop
      xl: 1536, // large screens
    },
  },
})

export default function HomePage({ records }) {
  return (
    <ThemeProvider theme={theme}>
      <Container></Container>
    </ThemeProvider>
  )
}

// export async function getStaticProps() {
//   const res = await fetch('http://localhost:5050/records/calibration-data')
//   const records = await res.json()

//   return {
//     props: {
//       records,
//     },
//   }
// }
