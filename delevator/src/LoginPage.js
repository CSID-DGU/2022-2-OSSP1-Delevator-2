import React from "react";
import "./LoginPage.css";

const LoginPage = () => {
  return (
    <div className="login-page-div">
      <div className="div">
        <div className="searchbargroup-div">
          <div className="borderline-div" />
          <b className="b">사용자 로그인</b>
        </div>
      </div>
      <div className="div1">
        <div className="searchbargroup-div">
          <div className="borderline-div" />
          <b className="b">관리자 로그인</b>
        </div>
      </div>
      <div className="site-name-div">
        <b className="delevator-b">Delevator</b>
      </div>
      <input className="input" type="text" placeholder="Enter User ID" />
      <div className="line2"></div>
      <div className="or-div">OR</div>
      <div className="line1"></div>
    </div>
  );
};

export default LoginPage;
