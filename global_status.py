"""
Global Status Component for AURA System
Shows Module 1 processing status across all pages
"""

import streamlit as st
from background_processor import get_background_status
from datetime import datetime

def show_global_processing_status():
    """Show Module 1 processing status in sidebar or header"""
    try:
        # Import here to avoid circular imports
        from background_processor import init_background_state
        init_background_state()
        
        bg_status = get_background_status()
        
        if bg_status['active'] or bg_status['result']:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🧠 AURA Module 1 Status")
            
            if bg_status['active']:
                # Show active processing
                st.sidebar.success("🔄 Processing video in background...")
                
                if bg_status['progress']:
                    progress = bg_status['progress']
                    progress_pct = progress['processed'] / max(progress['total_estimated'], 1)
                    st.sidebar.progress(progress_pct)
                    st.sidebar.caption(f"Processed {progress['processed']}/{progress['total_estimated']} frames")
                    
                    # Show current classification
                    if 'current_category' in progress:
                        category_emoji = {
                            'Critical': '🔴',
                            'Important': '🟡', 
                            'Normal': '🟢',
                            'Discard': '⚫'
                        }
                        emoji = category_emoji.get(progress['current_category'], '📊')
                        st.sidebar.caption(f"{emoji} Current: {progress['current_category']}")
                
                # Show elapsed time
                if bg_status['start_time']:
                    elapsed = datetime.now() - bg_status['start_time']
                    st.sidebar.caption(f"⏱️ Running for {elapsed.seconds//60}m {elapsed.seconds%60}s")
                
                # Quick navigation to Module 1
                if st.sidebar.button("👁️ View Processing Details", use_container_width=True):
                    st.switch_page("pages/01__Module_1.py")
            
            elif bg_status['result']:
                result = bg_status['result']
                
                if result.get('completed', False):
                    # Show completion status
                    st.sidebar.success("✅ Module 1 Processing Complete!")
                    
                    # Show key metrics
                    counts = result['counts']
                    processed = result['processed']
                    saved = counts["Critical"] + counts["Important"] + counts["Normal"]
                    reduction = result['reduction']
                    
                    st.sidebar.metric("Frames Processed", processed)
                    st.sidebar.metric("Write Reduction", f"{reduction:.1f}%")
                    
                    if result['video_created']:
                        st.sidebar.success("🎬 Video created successfully!")
                    
                    # Quick navigation to see results
                    if st.sidebar.button("📊 View Full Results", use_container_width=True):
                        st.switch_page("pages/01__Module_1.py")
                
                elif 'error' in result:
                    st.sidebar.error("❌ Module 1 Processing Failed")
                    st.sidebar.caption(f"Error: {result['error'][:50]}...")
                    
                    if st.sidebar.button("🔧 Check Error Details", use_container_width=True):
                        st.switch_page("pages/01__Module_1.py")
    
    except Exception as e:
        # Silently handle any errors to avoid breaking other pages
        pass

def show_compact_status():
    """Show a compact status indicator in the main content area"""
    try:
        from background_processor import init_background_state
        init_background_state()
        
        bg_status = get_background_status()
        
        if bg_status['active']:
            # Show active processing banner
            st.info("🔄 **Module 1** is processing video in the background. You can continue using other modules.")
            
            if bg_status['progress']:
                progress = bg_status['progress']
                progress_pct = progress['processed'] / max(progress['total_estimated'], 1)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.progress(progress_pct)
                with col2:
                    st.caption(f"{progress['processed']}/{progress['total_estimated']} frames")
                with col3:
                    if st.button("View Details", key="compact_view_details"):
                        st.switch_page("pages/01__Module_1.py")
        
        elif bg_status['result'] and bg_status['result'].get('completed', False):
            # Show completion banner
            result = bg_status['result']
            reduction = result['reduction']
            
            st.success(f"✅ **Module 1** processing complete! Achieved {reduction:.1f}% write reduction.")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption("Video analysis and optimization finished successfully.")
            with col2:
                if st.button("View Results", key="compact_view_results"):
                    st.switch_page("pages/01__Module_1.py")
    
    except Exception as e:
        # Silently handle any errors
        pass

def get_processing_summary():
    """Get a summary of current processing status for display"""
    try:
        from background_processor import init_background_state
        init_background_state()
        
        bg_status = get_background_status()
        
        if bg_status['active']:
            if bg_status['progress']:
                progress = bg_status['progress']
                progress_pct = progress['processed'] / max(progress['total_estimated'], 1)
                return {
                    'status': 'processing',
                    'message': f"Processing video... {progress_pct:.0%} complete",
                    'progress': progress_pct,
                    'details': f"{progress['processed']}/{progress['total_estimated']} frames"
                }
            else:
                return {
                    'status': 'processing',
                    'message': "Starting video processing...",
                    'progress': 0,
                    'details': "Initializing..."
                }
        
        elif bg_status['result']:
            result = bg_status['result']
            if result.get('completed', False):
                return {
                    'status': 'completed',
                    'message': f"Processing complete! {result['reduction']:.1f}% reduction achieved",
                    'progress': 1.0,
                    'details': f"Processed {result['processed']} frames"
                }
            elif 'error' in result:
                return {
                    'status': 'error',
                    'message': "Processing failed",
                    'progress': 0,
                    'details': result['error'][:100]
                }
        
        return {
            'status': 'idle',
            'message': "No active processing",
            'progress': 0,
            'details': ""
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': "Status unavailable",
            'progress': 0,
            'details': str(e)
        }
