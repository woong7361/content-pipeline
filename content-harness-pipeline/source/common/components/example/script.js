(function () {
  const stage = document.getElementById("stage");
  CommonSceneController.scaleStage(stage);
  addEventListener("resize", () => CommonSceneController.scaleStage(stage));
  addEventListener("orientationchange", () => CommonSceneController.scaleStage(stage));

  const scenes = CommonSceneController.createSceneController(stage);

  /* topbar는 scene을 직접 알지 못한다. common:scenechange를 듣고
     data-qa-label / data-progress만 읽는다 (followScenes 기본값) */
  const topbar = CommonTopbar.init(document.getElementById("topbar"), {
    menu: document.getElementById("courseMenu"),
    title: "공용 컴포넌트 조립 예시",
    step: "컴포넌트 소개",
    progress: 10,
    course: {
      gradeLabel: "예시 차시 목록",
      current: "example",
      lessons: [
        { no: 1, id: "example", title: "공용 컴포넌트 조립 예시" },
        { no: 2, title: "준비 중" },
        { no: 3, title: "준비 중" }
      ]
    },
    onHome: () => scenes.showScene("scene-intro"),
    onNavigate: href => console.log("navigate", href),
    onSoundChange: on => console.log("sound", on)
  });

  const debug = CommonDebugJumper.init(
    document.getElementById("debugPanel"),
    scenes,
    { toggle: document.getElementById("debugToggle") }
  );

  document.getElementById("goPractice").addEventListener("click", () => scenes.showScene("scene-practice"));
  document.getElementById("goIntro").addEventListener("click", () => scenes.showScene("scene-intro"));

  let value = "";
  const keypadRoot = document.getElementById("demoKeypad");
  const display = document.getElementById("demoDisplay");
  const stamp = document.getElementById("demoStamp");
  const speech = document.getElementById("practiceSpeech");
  const character = document.getElementById("practiceCharacter");

  function setDisplay(next) {
    display.textContent = next;
    CommonKeypad.displayTick(display);
  }

  CommonKeypad.build(keypadRoot, key => {
    if (key === "del") {
      value = value.slice(0, -1);
      setDisplay(value);
      return;
    }
    if (key === "enter") {
      if (value === "12") {
        CommonFeedbackLayer.showStamp(stamp, "correct", { hold: false });
        character.src = "./assets/student-volunteer.webp";
        character.alt = "손을 들고 기뻐하는 학생";
        CommonSpeechBubble.show(speech, "정답입니다! 이 조합을 나중에 단일 index.html 안으로 inline하면 됩니다.");
        topbar.setProgress(100); /* scene 중간에 오르는 진행률은 콘텐츠가 직접 부른다 */
      } else {
        CommonFeedbackLayer.showStamp(stamp, "wrong", { hold: false });
        character.src = "./assets/student-thinking.webp";
        character.alt = "생각하는 학생";
        CommonSpeechBubble.show(speech, "다시 생각해보세요. 지우기 키로 고친 뒤 확인할 수 있어요.");
      }
      value = "";
      setDisplay("");
      return;
    }
    value = (value + key).slice(-2);
    setDisplay(value);
  });

  addEventListener("common:scenechange", () => {
    CommonFeedbackLayer.hideStamp(stamp);
    debug.sync();
  });
})();
