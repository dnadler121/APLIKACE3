
const axis = document.getElementById("axis");

const drawA = document.getElementById("drawA");
const drawB = document.getElementById("drawB");

const intervalA = document.getElementById("intervalA");
const intervalB = document.getElementById("intervalB");
const overlap = document.getElementById("overlap");

let current = "A";

let start = null;

let data = {
A:null,
B:null
};

drawA.onclick = () => {

current = "A";

drawA.classList.add("active");
drawB.classList.remove("active");
};

drawB.onclick = () => {

current = "B";

drawB.classList.add("active");
drawA.classList.remove("active");
};

document.getElementById("clear").onclick = () => {

data.A = null;
data.B = null;

render();
};

document.querySelectorAll(".tick").forEach(tick => {

tick.addEventListener("click", function(e){

e.stopPropagation();

const value = parseInt(this.dataset.value);

if(start === null){
start = value;
return;
}

let a = start;
let b = value;

if(a>b){
[a,b] = [b,a];
}

data[current] = {a,b};

start = null;

render();

});

});

function valueToX(v){

const tick = document.querySelector(`.tick[data-value="${v}"]`);

return tick.offsetLeft;
}

function renderInterval(obj, el){

if(!obj){
el.classList.add("hidden");
return;
}

const left = valueToX(obj.a);
const right = valueToX(obj.b);

el.style.left = left + "px";
el.style.width = (right-left) + "px";

el.classList.remove("hidden");
}

function renderOverlap(){

const A = data.A;
const B = data.B;

if(!A || !B){
overlap.classList.add("hidden");
return;
}

const start = Math.max(A.a,B.a);
const end = Math.min(A.b,B.b);

if(start>=end){
overlap.classList.add("hidden");
return;
}

const left = valueToX(start);
const right = valueToX(end);

overlap.style.left = left + "px";
overlap.style.width = (right-left) + "px";

overlap.classList.remove("hidden");
}

function render(){

renderInterval(data.A, intervalA);
renderInterval(data.B, intervalB);

renderOverlap();
}

render();
