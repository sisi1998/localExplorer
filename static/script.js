document.addEventListener("DOMContentLoaded", () => {
    const baseApiUrl = "/explore";

    // Set default datetime to now
    const datetimePicker = document.getElementById("datetime-picker");
    const now = new Date();
    datetimePicker.value = now.toISOString().slice(0, 16);

    function formatDateTime(datetime) {
        const date = new Date(datetime);
        return date.toISOString().split('.')[0];
    }

    async function fetchData(datetime = null) {
        try {
            let apiUrl = baseApiUrl;
            
            // Add datetime parameter if provided
            if (datetime) {
                const formattedDateTime = formatDateTime(datetime);
                apiUrl += `?datetime_str=${formattedDateTime}`;
            }

            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error("Failed to fetch data");
            const data = await response.json();

            // Update time
            document.getElementById("time").textContent = 
                `Selected time: ${new Date(data.time).toLocaleString()}`;

            // Update weather data
            const location = data.current_conditions.location;
            const weather = data.current_conditions.weather;
            document.getElementById("location").textContent = 
                `${location.city}, ${location.country}`;
            document.getElementById("temperature").textContent = 
                weather.temperature.toFixed(1);
            document.getElementById("description").textContent = 
                weather.description;
            document.getElementById("wind_speed").textContent = 
                weather.wind_speed;
            document.getElementById("humidity").textContent = 
                weather.humidity;

            // Update activity suggestions
            const suggestions = data.suggestions;
            document.getElementById("summary").textContent = suggestions.summary;
            
            const activitiesContainer = document.getElementById("activities");
            activitiesContainer.innerHTML = "";
            
            suggestions.activities.forEach(activity => {
                const activityCard = document.createElement("div");
                activityCard.className = "activity-card";
                activityCard.innerHTML = `
                    <h3>${activity.name}</h3>
                    <p><strong>Type:</strong> ${activity.type}</p>
                    <p>${activity.description}</p>
                    <p><strong>Tips:</strong> ${activity.tips}</p>
                    <p><strong>Timing:</strong> ${activity.timing}</p>
                `;
                activitiesContainer.appendChild(activityCard);
            });
        } catch (error) {
            console.error("Error fetching data:", error);
            document.getElementById("summary").textContent = 
                "Error loading suggestions. Please try again later.";
        }
    }

    // Add event listener for the update button
    document.getElementById("update-time").addEventListener("click", () => {
        const selectedDateTime = datetimePicker.value;
        if (selectedDateTime) {
            fetchData(selectedDateTime);
        }
    });

    // Initial fetch
    fetchData();
});
