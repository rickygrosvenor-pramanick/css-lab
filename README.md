# CSS Lab Testing Repository

Sandbox Repository for Testing Concepts for LLMs for Well-being Project.

## Prerequisites

- Python 3.10.18
  * Easiest to set up an environment for CSS Work `conda create -n css-lab python=3.10.18`
- `pip`
- An OpenAI API key

## Installation

1. Clone the repo:
   ```
   git clone https://github.com/rickygrosvenor-pramanick/css-lab.git
   cd css-lab
   ```
2. Install Dependencies
   `pip install -r requirements.txt`
3. Configure `.env`
   `touch .env`
4. Add your OpenAI API Key in this format to .env
   `OPENAI_API_KEY="your-key-here"`
5. Run the Script
   `python main.py --turns NUM_WEEKS_TO_SIMULATE`

### Multi-Agent Life Simulation
1. Follow Steps 1-4 from [Installation](#installation) section above.
2. Run `python multi-agent-life-sim/multi-agent-life-sim.py --start-age START_AGE --end-age END_AGE`