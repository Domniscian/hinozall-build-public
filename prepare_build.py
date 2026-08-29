from pathlib import Path

root = Path("work")
home = root / "app/src/main/java/com/domniscian/app/ui/screens/HomeScreen.kt"
build = root / "app/build.gradle.kts"
text = home.read_text(encoding="utf-8")

if "private fun ActivityDayClock(" not in text:
    text = text.replace(
        "import androidx.compose.foundation.BorderStroke\n",
        "import androidx.compose.foundation.BorderStroke\nimport androidx.compose.foundation.Canvas\n",
        1,
    )
    text = text.replace(
        "import androidx.compose.ui.graphics.Color\n",
        "import androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.graphics.StrokeCap\nimport androidx.compose.ui.graphics.drawscope.Stroke\nimport androidx.compose.ui.graphics.nativeCanvas\nimport androidx.compose.ui.graphics.toArgb\n",
        1,
    )
    text = text.replace(
        "import androidx.compose.ui.unit.dp\n",
        "import androidx.compose.ui.unit.dp\nimport androidx.compose.ui.unit.sp\n",
        1,
    )
    text = text.replace(
        "import java.time.LocalDate\n",
        "import java.time.LocalDate\nimport java.time.ZoneId\nimport kotlin.math.cos\nimport kotlin.math.sin\n",
        1,
    )

    marker = '''            item {
                SectionHeader(
                    "Historique d’activité",'''
    replacement = '''            item {
                ActivityDayClock(periods = periods)
            }

            item {
                SectionHeader(
                    "Historique d’activité",'''
    if marker not in text:
        raise SystemExit("History marker not found: refusing to build the wrong UI source")
    text = text.replace(marker, replacement, 1)

    marker2 = '''@Composable
private fun SummaryStat(label: String, value: String, accent: Color, modifier: Modifier = Modifier) {'''
    clock = '''@Composable
private fun ActivityDayClock(periods: List<ActivityPeriod>) {
    val zone = remember { ZoneId.systemDefault() }
    val today = LocalDate.now(zone)
    val dayStart = remember(today, zone) { today.atStartOfDay(zone).toInstant().toEpochMilli() }
    val dayEnd = remember(today, zone) { today.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli() }
    val now = System.currentTimeMillis()
    val visiblePeriods = periods.mapNotNull { period ->
        val rawStart = period.startAt ?: return@mapNotNull null
        val rawEnd = period.endAt ?: now
        val start = rawStart.coerceAtLeast(dayStart)
        val end = rawEnd.coerceAtMost(dayEnd)
        if (end > start) start to end else null
    }
    val primary = MaterialTheme.colorScheme.primary
    val outline = MaterialTheme.colorScheme.outline
    val onSurface = MaterialTheme.colorScheme.onSurface
    val surfaceVariant = MaterialTheme.colorScheme.surfaceVariant
    val density = LocalDensity.current
    val textSizePx = with(density) { 11.sp.toPx() }
    val labelPaint = remember { android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG) }.apply {
        color = onSurface.toArgb()
        textAlign = android.graphics.Paint.Align.CENTER
        textSize = textSizePx
        typeface = android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT, android.graphics.Typeface.BOLD)
    }

    Panel(Modifier.fillMaxWidth(), PaddingValues(horizontal = 16.dp, vertical = 16.dp)) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("Aujourd’hui", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold)
            Spacer(Modifier.weight(1f))
            Text(
                if (visiblePeriods.isEmpty()) "Aucune activité" else "${visiblePeriods.size} session${if (visiblePeriods.size > 1) "s" else ""}",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Spacer(Modifier.height(12.dp))
        Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Canvas(Modifier.size(252.dp)) {
                val center = androidx.compose.ui.geometry.Offset(size.width / 2f, size.height / 2f)
                val radius = size.minDimension * 0.37f
                val arcRadius = radius - 3.dp.toPx()
                val arcTopLeft = androidx.compose.ui.geometry.Offset(center.x - arcRadius, center.y - arcRadius)
                val arcSize = androidx.compose.ui.geometry.Size(arcRadius * 2f, arcRadius * 2f)

                drawCircle(
                    color = surfaceVariant.copy(alpha = .55f),
                    radius = radius + 18.dp.toPx(),
                    center = center,
                )
                drawCircle(
                    color = outline.copy(alpha = .22f),
                    radius = radius,
                    center = center,
                    style = Stroke(width = 2.dp.toPx()),
                )

                for (hour in 0 until 24) {
                    val angle = Math.toRadians((hour * 15.0) - 90.0)
                    val major = hour % 3 == 0
                    val outer = radius + 10.dp.toPx()
                    val inner = radius + if (major) 1.dp.toPx() else 5.dp.toPx()
                    val start = androidx.compose.ui.geometry.Offset(
                        center.x + cos(angle).toFloat() * inner,
                        center.y + sin(angle).toFloat() * inner,
                    )
                    val end = androidx.compose.ui.geometry.Offset(
                        center.x + cos(angle).toFloat() * outer,
                        center.y + sin(angle).toFloat() * outer,
                    )
                    drawLine(
                        color = if (major) onSurface.copy(alpha = .58f) else outline.copy(alpha = .35f),
                        start = start,
                        end = end,
                        strokeWidth = if (major) 2.dp.toPx() else 1.dp.toPx(),
                        cap = StrokeCap.Round,
                    )
                }

                visiblePeriods.forEach { (start, end) ->
                    val span = (dayEnd - dayStart).coerceAtLeast(1L).toFloat()
                    val startFraction = ((start - dayStart).toFloat() / span).coerceIn(0f, 1f)
                    val endFraction = ((end - dayStart).toFloat() / span).coerceIn(0f, 1f)
                    val sweep = ((endFraction - startFraction) * 360f).coerceAtLeast(1.2f)
                    drawArc(
                        color = primary,
                        startAngle = -90f + startFraction * 360f,
                        sweepAngle = sweep,
                        useCenter = false,
                        topLeft = arcTopLeft,
                        size = arcSize,
                        style = Stroke(width = 12.dp.toPx(), cap = StrokeCap.Round),
                    )
                }

                listOf(0, 3, 6, 9, 12, 15, 18, 21).forEach { hour ->
                    val angle = Math.toRadians((hour * 15.0) - 90.0)
                    val labelRadius = radius - 23.dp.toPx()
                    val x = center.x + cos(angle).toFloat() * labelRadius
                    val y = center.y + sin(angle).toFloat() * labelRadius + textSizePx * .35f
                    drawContext.canvas.nativeCanvas.drawText(hour.toString().padStart(2, '0'), x, y, labelPaint)
                }

                drawCircle(color = primary, radius = 4.5.dp.toPx(), center = center)
                val currentFraction = ((now.coerceIn(dayStart, dayEnd) - dayStart).toFloat() / (dayEnd - dayStart).coerceAtLeast(1L).toFloat())
                val currentAngle = Math.toRadians((currentFraction * 360f - 90f).toDouble())
                drawLine(
                    color = onSurface.copy(alpha = .75f),
                    start = center,
                    end = androidx.compose.ui.geometry.Offset(
                        center.x + cos(currentAngle).toFloat() * (radius - 36.dp.toPx()),
                        center.y + sin(currentAngle).toFloat() * (radius - 36.dp.toPx()),
                    ),
                    strokeWidth = 2.dp.toPx(),
                    cap = StrokeCap.Round,
                )
            }
        }
    }
}

@Composable
private fun SummaryStat(label: String, value: String, accent: Color, modifier: Modifier = Modifier) {'''
    if marker2 not in text:
        raise SystemExit("Summary marker not found: refusing to build the wrong UI source")
    text = text.replace(marker2, clock, 1)

home.write_text(text, encoding="utf-8")

b = build.read_text(encoding="utf-8")
import re
b = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 11', b, count=1)
b = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.5.1"', b, count=1)
build.write_text(b, encoding="utf-8")

# Guardrails: fail CI if the expected corrections are absent.
checks = {
    "no-target refresh": "Aucune cible sélectionnée à actualiser.",
    "engine selector": "ObservationMode",
    "Hinozall": "HINOZALL_AWOKEN",
}
merged = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*.kt"))
for label, needle in checks.items():
    if needle not in merged:
        raise SystemExit(f"Missing required correction: {label}")

manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
if 'android:supportsPictureInPicture="true"' not in manifest or 'android:resizeableActivity="true"' not in manifest:
    raise SystemExit("PiP manifest correction missing")

print("Prepared Hinozall Awoken 3.5.1 modern source with activity clock.")
