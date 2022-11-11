import "./UserPage.css";

const UserPage = () => {
  return (
    <div className="user-page-div">
      <div className="site-name-div1">
        <b className="user-b">User</b>
      </div>
      <img className="image-2-icon" alt="" src="../image-2@2x.png" />
      <div className="frame-div">
        <b className="b">항목별 부정행위 의심 정도(%)</b>
      </div>
      <div className="group-div">
        <div className="frame-div1">
          <b className="b1">얼굴</b>
        </div>
        <div className="frame-div2">
          <b className="b2">책 및 교안</b>
        </div>
        <div className="frame-div3">
          <b className="b3">핸드폰</b>
        </div>
        <div className="frame-div4">
          <b className="b4">제3자</b>
        </div>
      </div>
      <div className="div5">의심</div>
      <div className="rectangle-div" />
      <div className="button-div">93.4</div>
      <div className="button-div1">13.7</div>
      <div className="button-div2" id="num">
        22.1
      </div>
      <div className="div6">32.5</div>
    </div>
  );
};

export default UserPage;
