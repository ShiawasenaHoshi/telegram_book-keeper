from __future__ import annotations


async def test_report_answers_with_summary_photo_and_document(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  await user.send("100")

  before = len(await user.messages())
  await user.send("📊 Отчет")
  produced = (await user.messages())[before:]

  assert any("ОТЧЕТ ЗА" in m.text for m in produced)
  assert any("РАСХОД ПО КАТЕГОРИЯМ" in m.text for m in produced)
  assert any("photo" in m.raw for m in produced)
  assert any("document" in m.raw for m in produced)
