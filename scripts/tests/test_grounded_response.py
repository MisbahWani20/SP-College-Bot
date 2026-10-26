from chatbot.llm_service import generate_grounded_response


def main():

    print("=" * 60)
    print("       GROUNDED RESPONSE TEST")
    print("=" * 60)

    question = "What is the duration and eligibility for BSc IT?"

    context = """
Official Cluster University Srinagar information:

Programme: BSc IT
Programme Level: Undergraduate
Duration: 4 years

Overview:
BSc IT is an undergraduate programme focused on
information technology and computing.

The programme covers areas related to computer
applications, information technology, programming,
databases, networking and other IT-related subjects.
"""

    print("\nQUESTION:")
    print(question)

    print("\nOFFICIAL CONTEXT:")
    print(context)

    answer = generate_grounded_response(
        question,
        context
    )

    print("\n" + "=" * 60)
    print("             FINAL ANSWER")
    print("=" * 60)

    if answer:
        print(answer)
    else:
        print("No grounded response generated.")


if __name__ == "__main__":
    main()