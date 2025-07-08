---
applyTo: "**"
---

# 🧠 Copilot Agent Instructions for Django + Wagtail Project

## 🐍 Framework
This project is built using **Django**, a high-level Python web framework that promotes rapid development and clean, pragmatic design. It also integrates **Wagtail CMS** for advanced content management capabilities.

---

## ✅ General Guidelines

- Follow **Django best practices**:
  - Use class-based views (`CBVs`) over function-based views unless otherwise justified.
  - Organize code into modular apps with clear separation of concerns.
  - Use `settings.py` or `settings/` packages with environment-specific settings.
  - Use `django-environ` or `python-decouple` for secure environment variable management.
  - Use `Prefetch`, `select_related`, or `annotate` to optimize query performance.
  - Use Django signals only if necessary; prefer explicit service calls.

- Use **Wagtail** only for content management features (e.g., Pages, Snippets, Documents).
  - Avoid mixing business logic into Wagtail `Page` models.
  - Use Wagtail’s `StreamField` for flexible content areas.
  - When exposing content via API, extend Wagtail's `api_fields` or use custom DRF serializers.

---

## 🧱 Project Structure Conventions

- Create separate apps for each functional domain (`users`, `onboarding`, `content`, etc.).
- Each app must include:
  - `models.py`: ORM definitions
  - `serializers.py`: DRF serializers
  - `views.py`: API views
  - `urls.py`: local routing
  - `tests/`: unit + integration tests
  - `admin.py`: admin/Wagtail integration if needed

---

## 🔐 Authentication & Permissions

- Use **JWT or token-based auth** for APIs (e.g., with `djangorestframework-simplejwt`).
- Admins authenticate via Wagtail’s `/admin/` interface.
- Custom roles (e.g., `admin`, `moderator`, `user`) must be handled via custom `User` model and DRF permissions.

---

## 📑 Wagtail-Specific Considerations

- Use `Page` models for editable content only (e.g., tutorials, welcome screens).
- Use `Snippet` models for reusable content blocks (e.g., focus areas, interest areas).
- Leverage Wagtail admin for translation support when applicable (e.g., `wagtail-modeltranslation`).
- When creating custom APIs for content, expose via `wagtail.api.v2` or build a separate DRF view layer.

---

## 🧪 Testing Guidelines

**All new features must include corresponding test cases.**

- Use `pytest` or Django’s `TestCase` framework.
- Cover:
  - Model logic (custom methods, signals)
  - API views and permissions
  - Serializers (validation, transformation)
  - Business logic (e.g., onboarding steps, OTP flows)

Structure example:
app_name/
├── tests/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_services.py
---

## 📦 Package Conventions

- Use only battle-tested, production-grade packages:
  - `wagtail`
  - `djangorestframework`
  - `django-environ`
  - `drf-spectacular` for OpenAPI documentation (if applicable)
  - `pytest`, `pytest-django`, `factory_boy`, `faker` for testing

---

## 🔁 Version Control & Commits

- Use conventional commit messages (`feat:`, `fix:`, `refactor:`, `test:`, etc.)
- Each commit must be **atomic** and accompanied by a meaningful message.

---

## 📌 Summary

You're working on a Django + Wagtail project. Follow Django best practices, keep Wagtail logic focused on content only, and **always write tests** for the features you implement. APIs should be clean, testable, and optimized. Organize the project in apps with well-defined responsibilities.