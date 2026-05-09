from unittest.mock import patch


class TestAssistantChat:
    @patch("app.services.assistant_service.OpenAI")
    def test_chat_returns_reply(self, mock_openai, client, test_analysis):
        mock_openai.return_value.chat.completions.create.return_value.choices[
            0
        ].message.content = "O score de saúde é 55."

        response = client.post(
            "/api/assistant/chat",
            json={"message": "Qual é o score?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    @patch("app.services.assistant_service.OpenAI")
    def test_chat_with_property_id(
        self, mock_openai, client, test_property, test_analysis
    ):
        mock_openai.return_value.chat.completions.create.return_value.choices[
            0
        ].message.content = "Resposta de teste."

        response = client.post(
            "/api/assistant/chat",
            json={
                "message": "Qual é o score?",
                "property_id": test_property.id,
            },
        )
        assert response.status_code == 200
        assert "reply" in response.json()

    def test_empty_message_returns_422(self, client):
        response = client.post(
            "/api/assistant/chat",
            json={"message": ""},
        )
        assert response.status_code == 422
