{% if installed %}

## Changes as compared to your installed version:

### Breaking Changes

### Changes

### Features

{% if version_installed.replace("v", "").replace(".","") | int < 4  %}

- Updated trackimo library to 0.1.16
  {% endif %}
  {% if version_installed.replace("v", "").replace(".","") | int < 3  %}
- Updated trackimo library to 0.1.15
  {% endif %}
  {% if version_installed.replace("v", "").replace(".","") | int < 2  %}
- Updated trackimo library to 0.1.13
  {% endif %}

### Bugfixes

{% if version_installed.replace("v", "").replace(".","") | int < 3  %}

- Fix for authorisation token refresh
  {% endif %}

---

{% endif %}
