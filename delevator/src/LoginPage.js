import "./LoginPage.css";

const LoginPage = () => {
  return (
    <div className="login-page-div">
      <div className="div7">
        <div className="searchbargroup-div">
          <div className="borderline-div" />
          <b className="b5">사용자 로그인</b>
        </div>
      </div>
      <div className="div8">
        <div className="searchbargroup-div">
          <div className="borderline-div" />
          <b className="b5">관리자 로그인</b>
        </div>
      </div>
      <div className="site-name-div2">
        <b className="delevator-b">Delevator</b>
      </div>
      <input className="input" type="text" placeholder="Enter User ID" />
      <div className="div9">
        <div className="or-div">OR</div>
      </div>
      <img className="line-icon" alt="" src="../line-1.svg" />
      <img className="line-icon1" alt="" src="../line-2.svg" />
    </div>
  );
};

export default LoginPage;
