/*
Copyright (c) 2023, CloudBlue Connect
All rights reserved.
*/
// prepare UI components

export const prepareDatabases = (databases) => {
  try {
    return databases.reduce((list, db) => `${list}<li class="list-item">
        <div class="list-item-content">
          <h4>${db.id} - ${db.name}</h4>
        </div>
      </li>`, '');
  } catch (e) { return ''; }
};

// render UI components
export const renderDatabases = (databases) => {
  const element = document.getElementById('databases');
  element.innerHTML = databases;
};

// render UI components - show/hide
export const showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

export const hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};
