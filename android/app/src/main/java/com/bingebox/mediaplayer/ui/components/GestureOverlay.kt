package com.bingebox.mediaplayer.ui.components

import androidx.compose.animation.*
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

@Composable
fun GestureOverlay(
    modifier: Modifier = Modifier,
    isLocked: Boolean = false,
    onSingleTap: () -> Unit,
    onDoubleTapSeek: (forward: Boolean) -> Unit,
    content: @Composable BoxScope.() -> Unit
) {
    var indicatorText by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(indicatorText) {
        if (indicatorText != null) {
            delay(800)
            indicatorText = null
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .pointerInput(isLocked) {
                detectTapGestures(
                    onTap = { onSingleTap() },
                    onDoubleTap = { offset ->
                        if (!isLocked) {
                            val isRight = offset.x > (size.width / 2)
                            onDoubleTapSeek(isRight)
                            indicatorText = if (isRight) "+10s ⏩" else "⏪ -10s"
                        }
                    }
                )
            }
    ) {
        content()

        // Center Gesture Indicator Badge
        AnimatedVisibility(
            visible = indicatorText != null,
            enter = fadeIn() + scaleIn(),
            exit = fadeOut() + scaleOut(),
            modifier = Modifier.align(Alignment.Center)
        ) {
            indicatorText?.let { text ->
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xCC151923),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF8B5CF6))
                ) {
                    Text(
                        text = text,
                        fontSize = 20.sp,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp)
                    )
                }
            }
        }
    }
}
