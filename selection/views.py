from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd


@api_view(["POST"])
def upload_file(request):
    postulantes = request.FILES.get("file")
    if postulantes:
        df = pd.read_excel(postulantes, sheet_name="POSTULADOS")
        postulados = df[df["DEPENDENCIA"] == "DIVISION DE BIBLIOTECA"].sort_values(
            by="PROMEDIO", ascending=False
        ).to_dict(orient="index")

        res = [student for student in postulados.values()]

        return Response({"data": res}, status=200)

    return Response({"message": "File not uploaded"}, status=400)
