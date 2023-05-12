import Proptypes from 'prop-types'
import { wrapper } from '../store/store'
import { Provider } from 'react-redux'

const App = ({ Component, ...rest }) => {
  const { store, props } = wrapper.useWrappedStore(rest)
  return (
    <Provider store={store}>
      <Component {...props.pageProps} />
    </Provider>
  )
}

App.Proptypes = {
  Component: Proptypes.elementType,
  store: Proptypes.object,
}

export default App
