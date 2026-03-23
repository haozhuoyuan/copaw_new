import { useState } from "react";
import {
  Modal,
  Input,
  Button,
  message,
  Spin,
  Typography,
  Tag,
  Space,
} from "antd";
import { Plus, Sparkles, Bot, Wand2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { agentsApi } from "../../api/modules/agents";
import type { GeneratedConfig } from "@/api/types/agents";
import styles from "./index.module.less";

const { Text } = Typography;
const { TextArea } = Input;

interface AgentCreatorProps {
  onSuccess?: () => void;
}

// Quick creation suggestions
const QUICK_SUGGESTIONS_ZH = [
  "创建一个代码书写智能体",
  "创建一个文案写作助手",
  "创建一个数据分析专家",
  "创建一个创意写作助手",
  "创建一个技术咨询顾问",
];

const QUICK_SUGGESTIONS_EN = [
  "Create a coding assistant",
  "Create a content writing helper",
  "Create a data analysis expert",
  "Create a creative writing assistant",
  "Create a technical consultant",
];

export default function AgentCreator({ onSuccess }: AgentCreatorProps) {
  const { t, i18n } = useTranslation();
  const [visible, setVisible] = useState(false);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [, setPreview] = useState<GeneratedConfig | null>(null);

  const isZh = i18n.language.startsWith("zh");
  const suggestions = isZh ? QUICK_SUGGESTIONS_ZH : QUICK_SUGGESTIONS_EN;

  const handleOpen = () => {
    setVisible(true);
    setDescription("");
    setPreview(null);
  };

  const handleClose = () => {
    setVisible(false);
    setDescription("");
    setPreview(null);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setDescription(suggestion);
    setPreview(null);
  };

  const handleCreate = async () => {
    if (!description.trim()) {
      message.error(t("agentCreator.descriptionRequired"));
      return;
    }

    try {
      setLoading(true);
      const response = await agentsApi.createAgentFromText({
        description: description.trim(),
        language: i18n.language.startsWith("zh") ? "zh" : "en",
      });

      message.success(response.message);
      handleClose();
      onSuccess?.();
    } catch (error: any) {
      console.error("Failed to create agent:", error);
      message.error(error.message || t("agentCreator.createFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Trigger Button - placed next to agent selector */}
      <Button
        type="link"
        icon={<Sparkles size={16} />}
        onClick={handleOpen}
        className={styles.creatorButton}
      >
        {t("agentCreator.title")}
      </Button>

      {/* Creation Modal */}
      <Modal
        title={
          <Space>
            <Wand2 size={20} />
            <span>{t("agentCreator.modalTitle")}</span>
          </Space>
        }
        open={visible}
        onCancel={handleClose}
        width={600}
        footer={[
          <Button key="cancel" onClick={handleClose}>
            {t("common.cancel")}
          </Button>,
          <Button
            key="create"
            type="primary"
            icon={<Plus size={16} />}
            loading={loading}
            onClick={handleCreate}
            disabled={!description.trim()}
          >
            {t("agent.create")}
          </Button>,
        ]}
      >
        <Spin spinning={loading}>
          <div className={styles.creatorContent}>
            {/* Description Input */}
            <div className={styles.inputSection}>
              <Text strong>{t("agentCreator.describeAgent")}</Text>
              <TextArea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={t("agentCreator.placeholder")}
                rows={3}
                className={styles.descriptionInput}
                maxLength={200}
                showCount
              />
            </div>

            {/* Quick Suggestions */}
            <div className={styles.suggestionsSection}>
              <Text type="secondary" className={styles.suggestionsLabel}>
                {t("agentCreator.quickSuggestions")}
              </Text>
              <Space size={[8, 8]} wrap>
                {suggestions.map((suggestion, index) => (
                  <Tag
                    key={index}
                    className={styles.suggestionTag}
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <Sparkles size={12} />
                    {suggestion}
                  </Tag>
                ))}
              </Space>
            </div>

            {/* Info Box */}
            <div className={styles.infoBox}>
              <Bot size={16} />
              <Text type="secondary" className={styles.infoText}>
                {t("agentCreator.infoText")}
              </Text>
            </div>
          </div>
        </Spin>
      </Modal>
    </>
  );
}
