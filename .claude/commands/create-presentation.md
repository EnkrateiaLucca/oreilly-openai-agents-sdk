I want you to create a remark style presentation (see this repo for reference if necessary: https://github.com/remarkjs/remark).

Below is a starting point reference example:
'''
<!DOCTYPE html>
<html>
  <head>
    <title>Presentation</title>
    <meta charset="utf-8">
    <style>
      @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);
      @import url(https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);
      @import url(https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);

      body { font-family: 'Droid Serif'; }
      h1, h2, h3 {
        font-family: 'Yanone Kaffeesatz';
        font-weight: normal;
      }
      .remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
    </style>
  </head>
  <body>
    <textarea id="source">
        class: center, middle
        # Presentation
        ---
        # Agenda
        1. Introduction
        2. Deep-dive
    </textarea>
    <script src="https://remarkjs.com/downloads/remark-latest.min.js">
    </script>
    <script>
      var slideshow = remark.create();
    </script>
  </body>
</html>

Create a presentation on [topic] using the Remark.js framework. The presentation should follow this structure:

1.  **Title Slide:**
    * Title: [Your Title]
    * Author: [Your Name]
    * Date: [Date]
In case this information is not provided you can just write the title and leave the rest as placeholder text as shown above.

2.  **Agenda Slide:**
    * Provide a table of contents outlining the main sections of the presentation.
    * Focus on single bullets (separated by '--' to introduce them gradually)
    * Make sure the full agenda actually fits in the screen and can be seen from the browser easily

3.  **Introduction Section:**
    * [Briefly introduce the topic and its importance.]

4.  **Core Content Sections:**
    * [Break down the main content into logical sections. For each section, specify the desired layout, such as "text with image," "two-column comparison," or "code snippets."]

5.  **Demo/Hands-on Section:**
    * Include a slide with a highlighted title for a demonstration or hands-on activity.
    * Always use a centralized layout with 'class: center, middle' at the top of the slide just after the separator '---'
    * Always use a highlighted section with html like this: 

      <h1>
       <span style="background-color: lightgreen">
          {Demo: The title of the DEMO GOES HERE}
       </span>
      </h1>

6.  **Q&A/Break Slide:**
    * Add a slide for questions and a short break.
    * Always use a centralized layout with 'class: center, middle' at the top of the slide just after the separator '---'

7.  **Conclusion Section:**
    * Summarize the key takeaways from the presentation.

8.  **Final Slides:**
    * A "Thank you" or final Q&A slide.
    * A "References" slide with relevant links and resources.
Of course. Here are three Remark.js/Markdown templates that provide structural snippets for an LLM to follow when integrating visuals.

1. **Template for Abstract Concept Diagrams**

This template is ideal for visualizing workflows, architectures, or abstract processes. The LLM should be instructed to generate a diagram based on the placeholder description.

---

# Title of the Concept

<div style="text-align: center; margin-top: 2em;">
  <img src="[path_to_image]" alt="A clear, minimalist flowchart diagram illustrating the steps of [the abstract concept], showing how [Component A] connects to [Component B] and leads to [Final Outcome]." style="width: 80%;">
</div>

---

10. **Template for Tangible Screenshots**

Use this template to show a real-world example of an application, a specific feature, or a snippet of code in action.

If its a single image, always make it centered to the slide using: 'class: center, middle' at the top of the slide.

Never place additional text or ## sections below a centered image. Always create an additional slide repeating the previous title with # and then the
additional section with ## if it must be associated with that part.

---

# Title for the Example

Here is a concrete example of [the feature being discussed]. Notice how [specific element] is highlighted.

<div style="text-align: center; margin-top: 1.5em;">
  <img src="[path_to_image]" alt="A high-resolution screenshot of the [Application Name] interface, with a red box highlighting the [specific button or feature] to demonstrate its function." style="width: 75%; border: 1px solid #ccc;">
</div>

---

11. **Template for Two-Column Layout (Text & Visual)**

---

# Title of Slide

<div style="display: flex; align-items: center; gap: 20px;">
  <div style="flex: 1;">
    - **Point One:** A brief explanation of the first key idea.
    --
    - **Point Two:** Details about the second important aspect.
    --
    - **Point Three:** Concluding thought or a call to action.
  </div>
  <div style="flex: 1; text-align: center;">
    <img src="[path_to_image]" alt="An illustrative icon or simple graphic that visually represents the core theme of '[Title of Slide]', such as a gear for processes or a lightbulb for ideas." style="width: 300px;">
  </div>
</div>

12. **Never Mix HTML and Markdown**

Never place markdown inside an html div like in this bad example:

# Why Agents Matter


<div ....>

    ### Capabilities
    - Use tools & APIs
    - Make decisions
    - Complete workflows
    - Maintain state

</div>

For these situations always either use only markdown, or use html with the <h1> or <h2> or <h3> tags.

---

Please ensure the presentation uses incremental bullet points (`--`) to reveal information sequentially and includes footnotes for any cited sources.

Below are the objectives of this presentation, instructions and the sole resources to use along with any other additional information you may need to create the final presentation:

$ARGUMENTS