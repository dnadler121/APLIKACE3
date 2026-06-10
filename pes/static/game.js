
const hintBtn = document.getElementById("hintBtn");
const hintText = document.getElementById("hintText");

if (hintBtn && hintText) {
    hintBtn.addEventListener("click", () => {
        hintText.classList.toggle("show");

        const paper = new Audio("https://actions.google.com/sounds/v1/foley/paper_rustle.ogg");
        paper.volume = 0.25;
        paper.play();
    });
}

const message = document.getElementById("message");
const unlock = document.getElementById("unlock");

if (message && message.classList.contains("success") && unlock) {

    unlock.classList.remove("hidden");

    const unlockSound = new Audio("https://actions.google.com/sounds/v1/cartoon/magic_chime.ogg");
    unlockSound.volume = 0.35;
    unlockSound.play();

    setTimeout(() => {
        unlock.classList.add("hidden");
    }, 1200);
}

if (message && message.classList.contains("danger")) {

    const heartbeat = new Audio("https://actions.google.com/sounds/v1/alarms/heartbeat.ogg");
    heartbeat.volume = 0.35;
    heartbeat.play();

    document.body.classList.add("shake-screen");

    setTimeout(() => {
        document.body.classList.remove("shake-screen");
    }, 700);
}

const paragraphs = document.querySelectorAll(".story-text p");

paragraphs.forEach((p, index) => {
    p.style.opacity = 0;

    setTimeout(() => {
        p.style.transition = "1s";
        p.style.opacity = 1;
        p.style.transform = "translateY(0px)";
    }, index * 900);
});

setTimeout(() => {
    const door = new Audio("https://actions.google.com/sounds/v1/doors/wood_door_creaking.ogg");
    door.volume = 0.18;
    door.play();
}, 2000);

const text = document.body.innerText.toLowerCase();

if (
    text.includes("vytí") ||
    text.includes("pes") ||
    text.includes("blata")
) {
    setTimeout(() => {
        const wolf = new Audio("https://actions.google.com/sounds/v1/animals/wolf_howl.ogg");
        wolf.volume = 0.22;
        wolf.play();
    }, 4500);
}

const flicker = document.createElement("div");
flicker.className = "lamp-flicker";
document.body.appendChild(flicker);

setInterval(() => {
    flicker.style.opacity = Math.random() * 0.16;
}, 200);
