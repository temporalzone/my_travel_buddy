import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import HomePage from './HomePage';
import ResetPasswordPage from './ResetPasswordPage';
import OtherComponents from './OtherComponents';

const App = () => {
  const params = new URLSearchParams(window.location.search);
  const resetToken = params.get('reset_token');

  return (
    <Router>
      <Switch>
        <Route path="/reset-password">
          {resetToken ? <ResetPasswordPage token={resetToken} /> : <HomePage />}
        </Route>
        <Route path="/other">
          <OtherComponents />
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Router>
  );
};

export default App;