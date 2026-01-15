document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function loadActivities() {
    try {
      const response = await fetch('/api/activities');
      const activities = await response.json();
      
      const activitiesList = document.getElementById('activities-list');
      const activitySelect = document.getElementById('activity');
      
      activitiesList.innerHTML = '';
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      
      for (const activity of activities) {
        // Use participants included in the activities response to avoid N+1 requests
        const participants = Array.isArray(activity.participants) ? activity.participants : [];
        
        // Create activity card
        const card = document.createElement('div');
        card.className = 'activity-card';
        
        // Activity title
        const titleEl = document.createElement('h4');
        titleEl.textContent = activity.name;
        
        // Activity description
        const descEl = document.createElement('p');
        descEl.textContent = activity.description;
        
        // Participants section
        const participantsSection = document.createElement('div');
        participantsSection.className = 'participants-section';
        
        const participantsHeader = document.createElement('h5');
        participantsHeader.textContent = `📋 Participants (${participants.length})`;
        participantsSection.appendChild(participantsHeader);
        
        if (participants.length > 0) {
          const ul = document.createElement('ul');
          ul.className = 'participants-list';
          
          participants.forEach(p => {
            const li = document.createElement('li');
            
            const emailSpan = document.createElement('span');
            emailSpan.className = 'participant-email';
            emailSpan.textContent = p.email;
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.title = 'Remove participant';
            deleteBtn.textContent = '🗑️';
            deleteBtn.dataset.activity = String(activity.id);
            deleteBtn.dataset.email = p.email;
            
            li.appendChild(emailSpan);
            li.appendChild(deleteBtn);
            ul.appendChild(li);
          });
          
          participantsSection.appendChild(ul);
        } else {
          const noParticipantsEl = document.createElement('p');
          noParticipantsEl.className = 'no-participants';
          noParticipantsEl.textContent = 'No participants yet. Be the first to sign up!';
          participantsSection.appendChild(noParticipantsEl);
        }
        
        card.appendChild(titleEl);
        card.appendChild(descEl);
        card.appendChild(participantsSection);
        
        activitiesList.appendChild(card);
        
        // Add to select dropdown
        const option = document.createElement('option');
        option.value = activity.id;
        option.textContent = activity.name;
        activitySelect.appendChild(option);
      }
      
      // Add event listeners to all delete buttons
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleDeleteParticipant);
      });
    } catch (error) {
      console.error('Error loading activities:', error);
      document.getElementById('activities-list').innerHTML = '<p>Error loading activities.</p>';
    }
  }
  
  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    const button = event.currentTarget;
    const activityId = button.getAttribute('data-activity');
    const email = button.getAttribute('data-email');
    
    if (!confirm(`Are you sure you want to unregister ${email} from ${activityId}?`)) {
      return;
    }
    
    try {
      const response = await fetch(
        `/api/activities/${encodeURIComponent(activityId)}/participants/${encodeURIComponent(email)}`,
        {
          method: 'DELETE'
        }
      );
      
      if (response.ok) {
        messageDiv.textContent = `Successfully unregistered ${email}`;
        messageDiv.className = 'success';
        messageDiv.classList.remove('hidden');
        
        // Reload activities to reflect the change
        await loadActivities();
        
        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add('hidden');
        }, 5000);
      } else {
        const result = await response.json();
        messageDiv.textContent = result.detail || 'Failed to unregister participant';
        messageDiv.className = 'error';
        messageDiv.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Error unregistering participant:', error);
      messageDiv.textContent = 'Failed to unregister participant. Please try again.';
      messageDiv.className = 'error';
      messageDiv.classList.remove('hidden');
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Reload activities to show the new participant
        await loadActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
  loadActivities();
});
