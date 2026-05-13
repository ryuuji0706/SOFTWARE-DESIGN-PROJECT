document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector(".circular-chart-container");
    const circle = container.querySelector(".circle");
    const percentageText = container.querySelector(".percentage");

    const budgetInput = document.getElementById("budgetInput");
    const spentInput = document.getElementById("spentInput");
    const remainingDisplay = document.getElementById("remainingDisplay");

    const radius = 15.9155;
    const circumference = 2 * Math.PI * radius;

    // Initialize circle
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = circumference;

    // Function to set circle color based on percentage
    function getCircleColor(percent) {
        if (percent <= 50) return "#4caf50";
        else if (percent <= 80) return "#ffeb3b";
        else return "#f44336";
    }

    // Function to update progress
    function setProgress(percent) {
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        circle.setAttribute("stroke", getCircleColor(percent));
        percentageText.textContent = `${Math.round(percent)}%`;
    }

    // Animate the progress
    function animateProgress(target, duration = 800) {
        let start = null;

        function step(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const percent = Math.min((progress / duration) * target, target);
            setProgress(percent);
            if (progress < duration) requestAnimationFrame(step);
        }

        requestAnimationFrame(step);
    }

    // Function to update chart and remaining dynamically
    function updateChart() {
        const budget = parseFloat(budgetInput.value) || 0;
        const spent = parseFloat(spentInput.value) || 0;
        const percent = budget > 0 ? Math.min((spent / budget) * 100, 100) : 0;
        remainingDisplay.textContent = Math.max(budget - spent, 0);
        animateProgress(percent);
    }

    // Initial animation
    updateChart();

    // Update when inputs change
    budgetInput.addEventListener("input", updateChart);
    spentInput.addEventListener("input", updateChart);
});