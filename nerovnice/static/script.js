const states = {
    axis1: { current: "A", start: null, A: null, B: null },
    axis2: { current: "A", start: null, A: null, B: null }
};

document.querySelectorAll(".mode").forEach(btn => {
    btn.addEventListener("click", () => {
        const axisId = btn.dataset.axis;
        const part = btn.dataset.part;

        states[axisId].current = part;

        document.querySelectorAll(`.mode[data-axis="${axisId}"]`).forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
    });
});

document.querySelectorAll(".clear").forEach(btn => {
    btn.addEventListener("click", () => {
        const axisId = btn.dataset.axis;
        states[axisId].A = null;
        states[axisId].B = null;
        states[axisId].start = null;
        renderAxis(axisId);
    });
});

document.querySelectorAll(".axis").forEach(axis => {
    axis.querySelectorAll(".tick").forEach(tick => {
        tick.addEventListener("click", e => {
            e.stopPropagation();

            const axisId = axis.id;
            const value = parseInt(tick.dataset.value);
            const st = states[axisId];

            if (st.start === null) {
                st.start = value;
                tick.classList.add("selectedTick");
                return;
            }

            let a = st.start;
            let b = value;

            if (a > b) {
                [a, b] = [b, a];
            }

            if (a !== b) {
                st[st.current] = { a, b };
            }

            st.start = null;
            axis.querySelectorAll(".tick").forEach(t => t.classList.remove("selectedTick"));
            renderAxis(axisId);
        });
    });
});

function valueToX(axis, value) {
    const tick = axis.querySelector(`.tick[data-value="${value}"]`);
    return tick.offsetLeft;
}

function renderInterval(axis, obj, el) {
    if (!obj) {
        el.classList.add("hidden");
        return;
    }

    const left = valueToX(axis, obj.a);
    const right = valueToX(axis, obj.b);

    el.style.left = left + "px";
    el.style.width = (right - left) + "px";
    el.classList.remove("hidden");
}

function renderOverlap(axis, st, el) {
    if (!st.A || !st.B) {
        el.classList.add("hidden");
        return;
    }

    const start = Math.max(st.A.a, st.B.a);
    const end = Math.min(st.A.b, st.B.b);

    if (start >= end) {
        el.classList.add("hidden");
        return;
    }

    const left = valueToX(axis, start);
    const right = valueToX(axis, end);

    el.style.left = left + "px";
    el.style.width = (right - left) + "px";
    el.classList.remove("hidden");
}

function renderAxis(axisId) {
    const axis = document.getElementById(axisId);
    const st = states[axisId];

    renderInterval(axis, st.A, axis.querySelector(".layerA"));
    renderInterval(axis, st.B, axis.querySelector(".layerB"));
    renderOverlap(axis, st, axis.querySelector(".overlap"));
}

renderAxis("axis1");
renderAxis("axis2");