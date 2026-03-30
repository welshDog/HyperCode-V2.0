import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import os

logger = logging.getLogger(__name__)

class AIRelay(commands.Cog):
    """AI-powered coaching and assistance for neurodivergent users."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    async def get_ai_response(self, prompt: str, system_prompt: str = None) -> str:
        """Get AI response from OpenAI or Ollama."""
        # Try OpenAI first if key exists
        if self.openai_key:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f'Bearer {self.openai_key}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': 'gpt-3.5-turbo',
                        'messages': [
                            {'role': 'system', 'content': system_prompt or 'You are a helpful ADHD coach.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'max_tokens': 500
                    }
                    async with session.post(
                        'https://api.openai.com/v1/chat/completions',
                        headers=headers,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"OpenAI failed: {e}")
        
        # Fallback to local Ollama
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'model': 'llama2',
                    'prompt': f"{system_prompt or 'You are a helpful ADHD coach.'}\n\nUser: {prompt}\n\nAssistant:",
                    'stream': False
                }
                async with session.post(
                    f'{self.ollama_host}/api/generate',
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('response', 'AI unavailable')
        except Exception as e:
            logger.error(f"Ollama failed: {e}")
        
        # Ultimate fallback
        return "AI services are currently unavailable. Try again later!"
    
    @app_commands.command(name="coach", description="Get ADHD productivity coaching")
    @app_commands.describe(topic="What do you need help with?")
    async def coach(self, interaction: discord.Interaction, topic: str):
        """ADHD coaching command."""
        await interaction.response.defer(thinking=True)
        
        try:
            system_prompt = """You are BROski Coach, an ADHD-specialized productivity assistant.
            Give short, actionable advice (max 3 bullet points).
            Be friendly, use emojis, and focus on quick wins.
            Never give long paragraphs - keep it bite-sized for ADHD minds."""
            
            response = await self.get_ai_response(topic, system_prompt)
            
            embed = discord.Embed(
                title="🧠 BROski Coach",
                description=response,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Powered by AI • Optimized for ADHD minds")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Coach command used by {interaction.user.name}: {topic}")
        
        except Exception as e:
            logger.error(f"Coach command failed: {e}")
            await interaction.followup.send(
                "❌ Coach is unavailable right now. Try again later!",
                ephemeral=True
            )
    
    @app_commands.command(name="hyperfocus", description="Get AI-powered focus session plan")
    @app_commands.describe(
        task="What task do you want to focus on?",
        duration="How long? (15, 25, 45, 60 minutes)"
    )
    async def hyperfocus(
        self,
        interaction: discord.Interaction,
        task: str,
        duration: int = 25
    ):
        """AI-powered hyperfocus planner."""
        await interaction.response.defer(thinking=True)
        
        if duration not in [15, 25, 45, 60]:
            await interaction.followup.send(
                "❌ Duration must be 15, 25, 45, or 60 minutes!",
                ephemeral=True
            )
            return
        
        try:
            system_prompt = f"""You are BROski Hyperfocus Planner.
            Break down the task into {duration}-minute micro-goals.
            Give exactly 3 mini-milestones.
            Each milestone should be 1 sentence, actionable, and achievable.
            Add motivational emoji to each point."""
            
            prompt = f"Task: {task}\nDuration: {duration} minutes\nCreate a focus plan."
            
            response = await self.get_ai_response(prompt, system_prompt)
            
            embed = discord.Embed(
                title=f"⚡ Hyperfocus Plan ({duration} min)",
                description=f"**Task:** {task}\n\n{response}",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="💡 Pro Tip",
                value="Use `/focus` to start tracking your session!",
                inline=False
            )
            embed.set_footer(text="Stay focused, BROski♾! 🔥")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Hyperfocus plan created for {interaction.user.name}: {task}")
        
        except Exception as e:
            logger.error(f"Hyperfocus command failed: {e}")
            await interaction.followup.send(
                "❌ Hyperfocus planner is unavailable right now.",
                ephemeral=True
            )
    
    @app_commands.command(name="anxietycheck", description="Quick anxiety reset tool")
    async def anxiety_check(self, interaction: discord.Interaction):
        """Anxiety management tool."""
        embed = discord.Embed(
            title="🧘 Anxiety Reset",
            description="**Quick grounding technique (30 seconds)**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="👀 5-4-3-2-1 Method",
            value=(
                "**5** things you can see\n"
                "**4** things you can touch\n"
                "**3** things you can hear\n"
                "**2** things you can smell\n"
                "**1** thing you can taste"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🌬️ Box Breathing",
            value=(
                "Breathe in: 4 seconds\n"
                "Hold: 4 seconds\n"
                "Breathe out: 4 seconds\n"
                "Hold: 4 seconds\n"
                "Repeat 4 times"
            ),
            inline=False
        )
        
        embed.set_footer(text="You've got this, BROski♾! 💪")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Anxiety check used by {interaction.user.name}")
    
    @app_commands.command(name="motivate", description="Get instant motivation boost")
    async def motivate(self, interaction: discord.Interaction):
        """Quick motivation command."""
        import random
        
        quotes = [
            "🔥 Your hyperfocus is a superpower, not a flaw!",
            "💪 Small progress is still progress, BROski!",
            "⚡ You don't need to be perfect, just consistent!",
            "🎯 Break it down, one tiny step at a time!",
            "🧠 ADHD isn't a barrier - it's your unique operating system!",
            "🚀 Start before you're ready. Momentum beats perfection!",
            "💎 Your brain works differently, and that's your advantage!",
            "🔥 Done is better than perfect, legend!",
            "⏱️ 5 minutes of action > 5 hours of planning!",
            "🐶♾️ You've got the BROski spirit! Let's GO!"
        ]
        
        quote = random.choice(quotes)
        
        embed = discord.Embed(
            title="💪 Motivation Boost",
            description=quote,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Believe in yourself, BROski♾!")
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Motivation sent to {interaction.user.name}")

async def setup(bot: commands.Bot):
    """Add AI relay cog to bot."""
    await bot.add_cog(AIRelay(bot))
