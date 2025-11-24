# Knowledge Bank Learning Module
# Interactive Tutorial for Content Generation
# ============================================
# STORY format for uDOS v1.4.0
#
# Usage:
#   PLAY memory/workflow/knowledge_learning.story
#   RUN memory/workflow/knowledge_learning.story --guided

STORY knowledge_learning {
  title: "Building the Knowledge Bank"
  description: "Interactive tutorial for survival guide generation using OK Assist"
  author: "uDOS Development Team"
  version: "1.4.0"
  difficulty: "intermediate"

  ## Chapter 1: Introduction
  CHAPTER welcome {
    title: "Welcome to Knowledge Generation"

    SCENE intro {
      DISPLAY """
      ╔════════════════════════════════════════════════════════════╗
      ║  🔮 uDOS Knowledge Bank Generation Tutorial               ║
      ║                                                            ║
      ║  Learn how to create comprehensive survival guides        ║
      ║  using OK Assist integration and GENERATE commands        ║
      ╚════════════════════════════════════════════════════════════╝
      """

      PANEL CREATE tutorial_info
      PANEL WRITE tutorial_info "What you'll learn:"
      PANEL WRITE tutorial_info "• Using GENERATE commands"
      PANEL WRITE tutorial_info "• OK Assist integration"
      PANEL WRITE tutorial_info "• Content organization"
      PANEL WRITE tutorial_info "• Quality validation"
      PANEL WRITE tutorial_info "• Cross-referencing topics"
      PANEL DISPLAY tutorial_info

      ASK $USER_NAME "What's your name?"
      PRINT "Welcome, $USER_NAME! Let's begin your journey."

      WAIT 2
    }

    SCENE goals {
      DISPLAY "Current Knowledge Bank Status:"
      GENERATE STATS knowledge/ --summary

      PRINT ""
      ASK $USER_GOAL "What type of content are you most interested in?"
      OPTION "🌊 Water procurement and purification"
      OPTION "🔥 Fire starting and maintenance"
      OPTION "🏠 Shelter construction"
      OPTION "🍖 Food foraging and preservation"
      OPTION "🧭 Navigation and signaling"
      OPTION "⚕️ Medical and first aid"
      OPTION "🔨 Tools and equipment"
      OPTION "📡 Communication systems"

      STORE $CHOSEN_CATEGORY = $USER_GOAL
      PRINT "Great choice! We'll focus on $CHOSEN_CATEGORY"
    }
  }

  ## Chapter 2: Understanding GENERATE Commands
  CHAPTER generate_basics {
    title: "GENERATE Command Basics"

    SCENE command_intro {
      PANEL CREATE generate_help
      PANEL WRITE generate_help "📚 GENERATE Command Syntax"
      PANEL WRITE generate_help "================================"
      PANEL WRITE generate_help ""
      PANEL WRITE generate_help "Format: GENERATE <type> <topic> [options]"
      PANEL WRITE generate_help ""
      PANEL WRITE generate_help "Types:"
      PANEL WRITE generate_help "  GUIDE   - Create comprehensive guide"
      PANEL WRITE generate_help "  DIAGRAM - Create SVG diagram"
      PANEL WRITE generate_help "  INDEX   - Create category index"
      PANEL WRITE generate_help ""
      PANEL WRITE generate_help "Options:"
      PANEL WRITE generate_help "  --mode ok-assist   Use OK Assistant"
      PANEL WRITE generate_help "  --mode placeholder Use templates"
      PANEL WRITE generate_help "  --style <style>    Diagram style"
      PANEL DISPLAY generate_help

      PRINT ""
      ASK $CONTINUE "Ready to try your first GENERATE command? (yes/no)"

      IF $CONTINUE == "yes" {
        GOTO first_generation
      } ELSE {
        PRINT "No problem! Take your time to review."
        WAIT 3
      }
    }

    SCENE first_generation {
      PRINT "Let's generate your first guide!"
      PRINT ""

      ASK $TOPIC "Enter a specific topic within $CHOSEN_CATEGORY:"
      PRINT "Generating guide for: $TOPIC"
      PRINT ""

      # Show the actual command
      PRINT "Command: GENERATE GUIDE $CHOSEN_CATEGORY/$TOPIC --mode ok-assist"
      PRINT ""

      ASK $EXECUTE "Execute this command? (yes/no)"

      IF $EXECUTE == "yes" {
        PRINT "✨ Initiating OK Assistant..."
        GENERATE GUIDE $CHOSEN_CATEGORY/$TOPIC --mode ok-assist
        PRINT "✅ Guide generated successfully!"

        # Show result
        PANEL CREATE generated_content
        READ knowledge/$CHOSEN_CATEGORY/$TOPIC.md | PANEL WRITE generated_content
        PANEL DISPLAY generated_content

        PRINT ""
        ASK $SATISFACTION "Are you happy with the result? (yes/no)"

        IF $SATISFACTION == "yes" {
          PRINT "Excellent! You've created your first guide."
          SCORE +10
        } ELSE {
          PRINT "Let's try refining it..."
          ASK $REFINEMENT "What would you like to improve?"
          PRINT "Tip: Use EDIT command to refine generated content"
          PRINT "Example: EDIT knowledge/$CHOSEN_CATEGORY/$TOPIC.md"
        }
      }
    }
  }

  ## Chapter 3: OK Assist Integration
  CHAPTER ok_assist {
    title: "Working with OK Assistant"

    SCENE assist_intro {
      DISPLAY """
      ╔════════════════════════════════════════════════════════════╗
      ║  🤖 OK Assistant Integration                              ║
      ║                                                            ║
      ║  OK Assistant uses advanced language models to generate   ║
      ║  comprehensive, accurate survival guides tailored to      ║
      ║  your needs.                                              ║
      ╚════════════════════════════════════════════════════════════╝
      """

      PRINT ""
      PRINT "OK Assist Features:"
      PRINT "✓ 800-1200 word comprehensive guides"
      PRINT "✓ Structured content (overview, materials, steps, safety)"
      PRINT "✓ Cross-referenced related topics"
      PRINT "✓ Technical diagrams in SVG format"
      PRINT "✓ Consistent Polaroid 8-color palette"
      PRINT ""

      ASK $LEARN_MORE "Would you like to see how OK Assist works? (yes/no)"

      IF $LEARN_MORE == "yes" {
        GOTO assist_demo
      }
    }

    SCENE assist_demo {
      PRINT "Let's explore OK Assist generation..."
      PRINT ""

      ASK $RESEARCH_TOPIC "Enter a research topic for OK Assistant:"
      PRINT "Querying OK Assistant about: $RESEARCH_TOPIC"

      # Use OK ASK to gather information
      OK ASK "Provide a comprehensive overview of $RESEARCH_TOPIC in the context of survival and self-sufficiency. Include key materials, steps, and safety considerations."

      PRINT ""
      ASK $USE_INFO "Would you like to create a guide from this information? (yes/no)"

      IF $USE_INFO == "yes" {
        GENERATE GUIDE $CHOSEN_CATEGORY/$RESEARCH_TOPIC --mode ok-assist
        PRINT "✅ Guide created and stored in knowledge bank"
        SCORE +15
      }
    }

    SCENE batch_generation {
      PRINT "You can also generate multiple guides at once!"
      PRINT ""

      ASK $BATCH_SIZE "How many related topics would you like to generate? (1-10)"

      PRINT "Great! Let's collect topics..."
      VAR $TOPICS = []

      LOOP $i FROM 1 TO $BATCH_SIZE {
        ASK $NEW_TOPIC "Topic #$i:"
        ARRAY_PUSH $TOPICS $NEW_TOPIC
      }

      PRINT ""
      PRINT "Generating $BATCH_SIZE guides..."

      FOREACH $topic IN $TOPICS {
        PRINT "  → $topic"
        GENERATE GUIDE $CHOSEN_CATEGORY/$topic --mode ok-assist
        WAIT 0.5  # Rate limiting
      }

      PRINT ""
      PRINT "✅ Batch generation complete!"
      PRINT "Total guides created: $BATCH_SIZE"
      SCORE +20
    }
  }

  ## Chapter 4: Quality & Organization
  CHAPTER quality_org {
    title: "Content Quality and Organization"

    SCENE quality_check {
      DISPLAY "Quality Standards for Knowledge Bank Guides:"
      PANEL CREATE standards
      PANEL WRITE standards "✓ 800-1200 word minimum"
      PANEL WRITE standards "✓ Clear structure (overview, materials, steps, safety)"
      PANEL WRITE standards "✓ Practical, actionable instructions"
      PANEL WRITE standards "✓ Safety warnings highlighted"
      PANEL WRITE standards "✓ Cross-references to related topics"
      PANEL WRITE standards "✓ Diagrams where applicable"
      PANEL DISPLAY standards

      PRINT ""
      PRINT "Let's validate your generated content..."

      # Run quality check
      VALIDATE knowledge/$CHOSEN_CATEGORY/ --metrics word-count,structure,cross-refs

      PRINT ""
      ASK $FIX_ISSUES "Any issues to address? (yes/no)"

      IF $FIX_ISSUES == "yes" {
        PRINT "Common fixes:"
        PRINT "1. Use EDIT to add missing sections"
        PRINT "2. Use LINK to add cross-references"
        PRINT "3. Use GENERATE DIAGRAM to add visuals"
      }
    }

    SCENE tagging {
      PRINT "Let's add tags and metadata to improve discoverability..."
      PRINT ""

      ASK $TAG_TOPICS "Enter tags for your guides (comma-separated):"

      PRINT "Applying tags: $TAG_TOPICS"

      # Apply tags to category
      TAG knowledge/$CHOSEN_CATEGORY/*.md --add $TAG_TOPICS

      PRINT "✅ Tags applied!"
      PRINT ""
      PRINT "Your guides are now:"
      PRINT "• Searchable by tag"
      PRINT "• Grouped by category"
      PRINT "• Cross-referenced"

      SCORE +10
    }

    SCENE cross_reference {
      PRINT "Cross-referencing connects related topics..."
      PRINT ""

      ASK $LINK_FROM "Select a guide to add cross-references to:"
      ASK $LINK_TO "Enter related topics (comma-separated):"

      PRINT "Creating links..."
      LINK knowledge/$CHOSEN_CATEGORY/$LINK_FROM.md --to $LINK_TO

      PRINT "✅ Cross-references created!"
      PRINT "Guides are now interconnected for better learning"

      SCORE +15
    }
  }

  ## Chapter 5: Mission Completion
  CHAPTER completion {
    title: "Completing Your Mission"

    SCENE progress_review {
      DISPLAY """
      ╔════════════════════════════════════════════════════════════╗
      ║  📊 Progress Review                                       ║
      ╚════════════════════════════════════════════════════════════╝
      """

      # Show comprehensive stats
      GENERATE STATS knowledge/ --detailed

      PRINT ""
      PRINT "Your contributions:"
      PRINT "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

      MISSION STATUS complete_knowledge_bank

      PRINT ""
      ASK $CONTINUE_MISSION "Continue working towards 1,000 guides? (yes/no)"

      IF $CONTINUE_MISSION == "yes" {
        PRINT "Excellent! Use these workflows:"
        PRINT "• RUN workflow/knowledge_generation.uscript"
        PRINT "• PLAY workflow/knowledge_learning.story"
        PRINT "• MISSION START complete_knowledge_bank"
      }
    }

    SCENE celebration {
      IF $SCORE >= 50 {
        DISPLAY """
        ╔════════════════════════════════════════════════════════════╗
        ║  🎉 CONGRATULATIONS!                                      ║
        ║                                                            ║
        ║  You've mastered knowledge generation!                    ║
        ║  Score: $SCORE points                                     ║
        ║                                                            ║
        ║  You're now ready to contribute to the complete           ║
        ║  knowledge bank. Keep generating!                         ║
        ╚════════════════════════════════════════════════════════════╝
        """

        ACHIEVEMENT UNLOCK "Knowledge Master"
        CERTIFICATE GENERATE "Knowledge Generation - $USER_NAME"
      } ELSE {
        PRINT "Keep practicing! Try generating more guides to increase your score."
      }

      PRINT ""
      PRINT "Next steps:"
      PRINT "1. Generate more content in your chosen category"
      PRINT "2. Try other categories to diversify"
      PRINT "3. Help review and improve existing guides"
      PRINT "4. Share knowledge with the community"
      PRINT ""
      PRINT "Thank you for building the knowledge bank, $USER_NAME!"
    }
  }

  ## Story Configuration
  config {
    allow_skip: true
    save_progress: true
    replay_enabled: true
    score_tracking: true
    achievements: true
  }
}

# Story Metadata
metadata {
  tags: ["tutorial", "knowledge", "generation", "ok-assist", "workflow"]
  difficulty: "intermediate"
  estimated_time: "30-45 minutes"
  prerequisites: ["basic_cli_usage", "ok_commands"]
  learning_objectives: [
    "Use GENERATE commands effectively",
    "Integrate OK Assistant for content creation",
    "Organize and tag knowledge content",
    "Create cross-referenced guide networks",
    "Track mission progress"
  ]
}
