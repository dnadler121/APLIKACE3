function formatTime(total) {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
}

const timer = document.getElementById("timer");

if (timer) {
    let seconds = Number(timer.dataset.seconds || 0);
    timer.textContent = formatTime(seconds);

    setInterval(() => {
        seconds -= 1;
        timer.textContent = formatTime(Math.max(seconds, 0));

        if (seconds <= 60) {
            timer.style.color = "#ff3355";
            timer.style.textShadow = "0 0 18px #ff3355";
        }

        if (seconds <= 0) {
            window.location.href = "/gameover?reason=Čas vypršel. Kontrola dorazila.";
        }
    }, 1000);
}

const hintButton = document.getElementById("hintButton");
const hintText = document.getElementById("hintText");

if (hintButton && hintText) {
    hintButton.addEventListener("click", () => {
        hintText.classList.toggle("show");
    });
}

const flash = document.getElementById("flash");
const transition = document.getElementById("successTransition");

if (flash && flash.classList.contains("success") && transition) {
    transition.classList.remove("hidden");
    setTimeout(() => {
        transition.classList.add("hidden");
    }, 1100);
}
