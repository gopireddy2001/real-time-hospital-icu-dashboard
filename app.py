{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "#Streamlit+ngrok\n",
        "#install require packages\n",
        "!pip install streamlit pyngrok --quiet\n",
        "\n"
      ],
      "metadata": {
        "id": "R8TNcCK9cMWe"
      },
      "execution_count": 47,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "!ngrok config add-authtoken 2yvv18F66iu28ybiek7AHS3tg5Y_7k9AL4TaMzjCZLxF8vNHL\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "4M3a-qLv2v-J",
        "outputId": "3baa5a42-ed8b-4554-bcb9-9d60285d659a"
      },
      "execution_count": 48,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Authtoken saved to configuration file: /root/.config/ngrok/ngrok.yml\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "%%writefile app.py\n",
        "import streamlit as st\n",
        "import pandas as pd\n",
        "\n",
        "st.title(\"Hospital ICU Occupancy Comparison Dashboard\")\n",
        "\n",
        "# Load datasets\n",
        "adult = pd.read_csv(\"/content/adult_icu_cleaned.csv\")\n",
        "pediatric = pd.read_csv(\"/content/pediatric_icu_cleaned.csv\")\n",
        "\n",
        "# Convert to datetime\n",
        "adult['date'] = pd.to_datetime(adult['date'])\n",
        "pediatric['date'] = pd.to_datetime(pediatric['date'])\n",
        "\n",
        "# Merge on state + date\n",
        "df = pd.merge(adult, pediatric, on=[\"state\", \"date\"], how=\"inner\")\n",
        "\n",
        "# Select state\n",
        "states = df['state'].unique()\n",
        "selected_state = st.sidebar.selectbox(\"Select State\", sorted(states))\n",
        "\n",
        "# Filter by state\n",
        "state_data = df[df['state'] == selected_state].sort_values('date')\n",
        "\n",
        "# Date range filter\n",
        "min_date = state_data['date'].min()\n",
        "max_date = state_data['date'].max()\n",
        "\n",
        "start_date, end_date = st.sidebar.date_input(\n",
        "    \"Select Date Range\",\n",
        "    [min_date, max_date],\n",
        "    min_value=min_date,\n",
        "    max_value=max_date\n",
        ")\n",
        "\n",
        "# Filter by date\n",
        "filtered_data = state_data[\n",
        "    (state_data['date'] >= pd.to_datetime(start_date)) &\n",
        "    (state_data['date'] <= pd.to_datetime(end_date))\n",
        "]\n",
        "\n",
        "# Show metrics\n",
        "latest = filtered_data.iloc[-1]\n",
        "st.metric(label=f\"Adult ICU Occupancy in {selected_state}\", value=f\"{latest['adult_icu_occupancy_percent']}%\")\n",
        "st.metric(label=f\"Pediatric ICU Occupancy in {selected_state}\", value=f\"{latest['pediatric_icu_occupancy_percent']}%\")\n",
        "\n",
        "# Line chart\n",
        "st.line_chart(\n",
        "    filtered_data.set_index('date')[\n",
        "        ['adult_icu_occupancy_percent', 'pediatric_icu_occupancy_percent']\n",
        "    ]\n",
        ")\n",
        "\n",
        "# ✅ Download button\n",
        "st.download_button(\n",
        "    label=\"Download ICU Data as CSV\",\n",
        "    data=filtered_data.to_csv(index=False).encode('utf-8'),\n",
        "    file_name=f\"{selected_state}_icu_data.csv\",\n",
        "    mime='text/csv'\n",
        ")\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "zUABuExt9b0E",
        "outputId": "00936e30-791c-4e25-87ac-674f3fa22a06"
      },
      "execution_count": 49,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Overwriting app.py\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "from pyngrok import ngrok\n",
        "import subprocess\n",
        "\n",
        "# Kill existing tunnels\n",
        "ngrok.kill()\n",
        "\n",
        "# Start the Streamlit app\n",
        "process = subprocess.Popen(['streamlit', 'run', 'app.py'])\n",
        "\n",
        "# Start a new ngrok tunnel (make sure this line is after importing ngrok!)\n",
        "public_url = ngrok.connect(8501, bind_tls=True)\n",
        "print(f\"🚀 Your Streamlit app is live at: {public_url}\")\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "IRkhEKfP5076",
        "outputId": "98ac4c43-0481-43d9-f334-4a0e4e2ca679"
      },
      "execution_count": 50,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "🚀 Your Streamlit app is live at: NgrokTunnel: \"https://5a5a-34-30-133-126.ngrok-free.app\" -> \"http://localhost:8501\"\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "\n"
      ],
      "metadata": {
        "id": "ZasTfs4O9E3s"
      },
      "execution_count": 50,
      "outputs": []
    }
  ]
}